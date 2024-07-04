import fastapi.testclient

from src import sql_api

def test_users__create(db_api, ox_cluster, client, log):
    # At the beginning of time, database is empty, random users accepted and are admins
    response = client.get("/users", auth=("useless", "useless"))
    assert response.status_code == 200
    assert response.json() == []
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
    assert response.status_code == 200
    assert response.json() == [{"name": "first_admin", "uuid": uuid, "is_admin": True}]

    # without auth, we got a 401 error
    response = client.post(
        "/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
    )
    assert response.status_code == 401

    # With auth, but with the wrong password, still fails
    response = client.post(
        "/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
        auth=("first_admin", "wrong_password"),
    )
    assert response.status_code == 401

    # With auth, but creating a user that already exists (and is myself, by the way)
    # will fail
    response = client.post(
        "/users",
        json={"name": "first_admin", "password": "toto", "is_admin": False},
        auth=("first_admin", "toto"),
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}


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


def test_domains__create_successful(db_api_session, log, client):
    """Succesfully create domain."""

    response = client.post(
        "/domains",
        json={
            "context_name": "context",
            "name": "domain",
            "features": ["mailbox", "webmail", "alias"],
        },
        auth=("", ""),
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    assert response.json() == {
        "name": "domain",
        "features": ["mailbox", "webmail", "alias"],
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": "context",
    }


def test_allows__create_allows(db_api_session, log, client):
    """Create "allows" object, granting an user management permissions to a domain."""

    # Create first admin for later auth
    auth = ("admin", "admin_password")
    sql_api.create_user(db_api_session, name=auth[0], password=auth[1], is_admin=True)

    # Create user and domain before access
    user = sql_api.create_user(db_api_session, name="user", password="password", is_admin=False)
    domain = sql_api.create_domain(
        db_api_session,
        name="domain",
        features=[],
    )

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

    # Delete allows
    response = client.delete(f"/allows/{domain.name}/{user.name}", auth=auth)
    assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT
    assert response.content == b""
