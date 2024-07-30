import fastapi.testclient

from .. import sql_api


def test_users__create(db_api, ox_cluster, client, log):
    # At the beginning of time, database is empty, random users are
    # accepted and are admins
    response = client.get("/users", auth=("useless", "useless"))
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == []

    # If we GET the user, it is not found
    response = client.get("/users/first_admin", auth=("useless", "useless"))
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    response = client.post(
        "/users",
        json={"name": "first_admin", "password": "toto", "is_admin": True},
        auth=("useless", "useless"),
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    # TODO : Comment piloter la génération des uuid depuis les tests pour les rendre prédictibles ?
    uuid = response.json()["uuid"]
    assert response.json() == {"name": "first_admin", "uuid": uuid, "is_admin": True}

    # Database is not empty anymore, only admins can do admin requests
    response = client.get("/users", auth=("first_admin", "toto"))
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == [{"name": "first_admin", "uuid": uuid, "is_admin": True}]

    # Check we can get the user we newly created
    response = client.get("/users/first_admin", auth=("first_admin", "toto"))
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {"name": "first_admin", "uuid": uuid, "is_admin": True}

    # If we GET a user that does not exist
    response = client.get("/users/nobody", auth=("first_admin", "toto"))
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # without auth, we got a 401 error
    response = client.post(
        "/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
    )
    assert response.status_code == fastapi.status.HTTP_401_UNAUTHORIZED

    # With auth, but with the wrong password, still fails
    response = client.post(
        "/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
        auth=("first_admin", "wrong_password"),
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # With auth, but creating a user that already exists (and is myself, by the way)
    # will fail
    response = client.post(
        "/users",
        json={"name": "first_admin", "password": "toto", "is_admin": False},
        auth=("first_admin", "toto"),
    )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT
    assert response.json() == {"detail": "User already exists"}


def test__update_a_user(log, client, admin):
    auth = (admin["user"], admin["password"])

    # If patch a user without the correct creds -> forbidden
    response = client.patch(
        "/users/does-not-exist",
        json={"password": "something"},
        auth=("not-a-user", "not-a-password"),
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # If patch a user that does not exist -> not found
    response = client.patch(
        "/users/does-not-exist",
        json={"password": "burps"},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # We create a normal user, so that we can modify it later
    response = client.post(
        "/users/",
        json={
            "name": "normal",
            "password": "toto",
            "is_admin": False,
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # Vérifier que l'utilisateur n'est pas admin
    response = client.get(
        "/users/normal",
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert not response.json()["is_admin"]

    # We can change the is_admin
    response = client.patch(
        "/users/normal",
        json={"is_admin": True},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK

    # Vérifier que l'utilisateur est bien devenu admin
    response = client.get(
        "/users/normal",
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json()["is_admin"]

    # On lui retire ses droits d'admin
    response = client.patch(
        "/users/normal",
        json={"is_admin": False},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK

    # Verifier qu'on peut obtenir un token avec l'ancien mot de passe
    response = client.get(
        "/token",
        auth=("normal", "toto"),
    )
    assert response.status_code == fastapi.status.HTTP_200_OK

    # We can set a new password
    response = client.patch(
        "/users/normal",
        json={"password": "coincoin"},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK

    # Verifier qu'on peut obtenir un token avec le nouveau mot de passe
    response = client.get(
        "/token",
        auth=("normal", "coincoin"),
    )
    assert response.status_code == fastapi.status.HTTP_200_OK


def test_delete_user(db_api_session, log, client, admin):
    """Check that we can delete a user and that it will remove all the
    associated allows."""
    auth = (admin["user"], admin["password"])

    # FIXME fixture
    # First, we create a normal user
    response = client.post(
        "/users/",
        json={
            "name": "normal",
            "password": "toto",
            "is_admin": False,
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # FIXME fixture
    # We create a firt domain
    response = client.post(
        "/domains/",
        json={
            "name": "domaine-1",
            "features": ["mailbox"],
            "context_name": "useless",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # FIXME fixture
    # We create a second domain
    response = client.post(
        "/domains/",
        json={
            "name": "domaine-2",
            "features": ["mailbox"],
            "context_name": "useless",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # FIXME fixture
    # Then we allow the user on two domains
    response = client.post(
        "/allows/",
        json={
            "user": "normal",
            "domain": "domaine-1",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # FIXME fixture
    # The second domain
    response = client.post(
        "/allows/",
        json={
            "user": "normal",
            "domain": "domaine-2",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED

    # Check that we can fetch the two allows
    response = client.get(
        "/allows/",
        params={
            "username": "normal",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    items = response.json()
    assert len(items) == 2
    assert {"domain": "domaine-1", "user": "normal"} in items
    assert {"domain": "domaine-2", "user": "normal"} in items

    # If we try to delete a user without the prems -> forbiden
    response = client.delete(
        "/users/normal",
        auth=("normal", "toto")
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # If we try to delete a user that does not exist -> not found
    response = client.delete(
        "/users/not-a-user",
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # If we delete the user -> ok, no content
    response = client.delete(
        "/users/normal",
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT

    # And now, if we fetch the user -> not found
    response = client.get(
        "/users/normal",
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # And now, if we fetch the allows -> empty list
    response = client.get(
        "/allows",
        params={
            "username": "normal",
        },
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert len(response.json()) == 0


def test_domains__create_fails_no_name(db_api_session, log, client):
    """Cannot create domain with no name."""

    response = client.post(
        "/domains",
        json={
            "context_name": "context",
            "name": None,
            "features": ["mailbox", "webmail", "alias"],
        },
        auth=("useless", "useless"),
    )
    assert response.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json() == {
        "detail": [
            {
                "type": "string_type",
                "loc": ["body", "name"],
                "msg": "Input should be a valid string",
                "input": None,
            }
        ]
    }


def test_domains__create_successful(db_api_session, log, client, admin):
    """Succesfully create domain."""

    # La creation d'un domaine par un admin fonctionne.
    response = client.post(
        "/domains",
        json={
            "context_name": "context",
            "name": "domain",
            "features": ["mailbox", "webmail", "alias"],
        },
        auth=(admin["user"], admin["password"]),
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    no_test = {"code": "no_test", "detail": "Did not check yet"}
    assert response.json() == {
        "name": "domain",
        "valid": False,
        "state": "new",
        "features": ["mailbox", "webmail", "alias"],
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": "context",
        "domain_exist": {"ok": False, "errors": [no_test]},
        "mx": {"ok": False, "errors": [no_test]},
        "cname_imap": {"ok": False, "errors": [no_test]},
        "cname_smtp": {"ok": False, "errors": [no_test]},
        "cname_webmail": {"ok": False, "errors": [no_test]},
        "spf": {"ok": False, "errors": [no_test]},
        "dkim": {"ok": False, "errors": [no_test]},
    }

    # La creation d'un deuxieme domaine par un admin, dans le même contexte
    # fonctionne aussi (le second domaine ne suit pas le même chemin de code,
    # car le contexte existe déjà)
    response = client.post(
        "/domains",
        json={
            "context_name": "context",
            "name": "domain2",
            "features": ["mailbox", "webmail", "alias"],
        },
        auth=(admin["user"], admin["password"]),
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED


def test_allows__create_allows(db_api_session, log, client):
    """Create "allows" object, granting an user management permissions to a domain."""

    # Create first admin for later auth
    auth = ("admin", "admin_password")
    sql_api.create_user(db_api_session, name=auth[0], password=auth[1], is_admin=True)

    # If we GET all the domains, we get an empty list
    response = client.get("/domains/", auth=("admin", "admin_password"))
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == []

    # Create user and domain before access
    user = sql_api.create_user(db_api_session, name="user", password="password", is_admin=False)
    domain = sql_api.create_domain(
        db_api_session,
        name="domain",
        features=[],
    )

    # If we GET all the domains, we get the one newly created
    response = client.get("/domains/", auth=("admin", "admin_password"))
    assert response.status_code == fastapi.status.HTTP_200_OK
    infos = response.json()
    assert len(infos) == 1
    assert infos[0]["name"] == "domain"

    # Create allows for this user on this domain
    response = client.post(
        "/allows/", json={"domain": domain.name, "user": user.name}, auth=auth
    )

    assert response.status_code == fastapi.status.HTTP_201_CREATED
    assert response.json() == {"user": user.name, "domain": domain.name}

    # GET list of "allows" should return 1 result
    assert len(client.get("/allows/", auth=auth).json()) == 1


def test_allows__delete_allows(db_api_session, log, client):
    """Delete "allows" object."""

    # Create first admin for later auth
    auth = ("admin", "admin_password")
    sql_api.create_user(db_api_session, name=auth[0], password=auth[1], is_admin=True)

    # Create allows and related user and domain
    user = sql_api.create_user(db_api_session, name="user", password="password", is_admin=False)
    domain = sql_api.create_domain(
        db_api_session,
        name="domain",
        features=[],
    )
    sql_api.allow_domain_for_user(
        db_api_session,
        user=user.name,
        domain=domain.name,
    )

    # Try to delete allow for an invalid user
    response = client.delete(f"/allows/{domain.name}/invalid_user", auth=auth)
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Try to delete allow for an invalid domain
    response = client.delete(f"/allows/invalid_domain/{user.name}", auth=auth)
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Delete allows
    response = client.delete(f"/allows/{domain.name}/{user.name}", auth=auth)
    assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT
    assert response.content == b""

    # Try to delete an allow that does not exist (but the user and the domain
    # exist)
    response = client.delete(f"/allows/{domain.name}/{user.name}", auth=auth)
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
