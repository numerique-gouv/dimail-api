import fastapi.testclient
import pytest

from .. import main, sql_api, sql_dovecot

client = fastapi.testclient.TestClient(main.app)


@pytest.fixture(scope="function")
def my_user(ox_cluster, db_api, log):
    user = "bidibule"
    domain = "tutu.net"

    # Database is empty, fake auth, creating the first admin
    res = client.post(
        "/admin/users",
        json={"name": "admin", "password": "admin", "is_admin": True},
        auth=("useless", "useless"),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    # Now, we can create our non-admin user
    res = client.post(
        "/admin/users/",
        json={"name": user, "password": "toto", "is_admin": False},
        auth=("admin", "admin"),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    res = client.post(
        "/admin/domains/",
        json={
            "name": domain,
            "features": ["webmail", "mailbox"],
            "context_name": "dimail",
        },
        auth=("admin", "admin"),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    ctx = ox_cluster.get_context_by_name("dimail")
    assert domain in ctx.domains

    res = client.post(
        "/admin/allows/",
        json={"user": user, "domain": domain},
        auth=("admin", "admin"),
    )
    assert res.status_code == fastapi.status.HTTP_201_CREATED

    res = client.get("/token/", auth=(user, "toto"))
    assert res.status_code == 200

    token = res.json()["access_token"]
    yield {"user": user, "domains": [domain], "token": token}


def test_create_mailbox(ox_cluster, my_user, db_dovecot_session):
    token = my_user["token"]

    response = client.post(
        "/domains/{domain_name}/mailboxes",
        json={
            "email": "address@tutu.net",
            "surName": "Essai",
            "givenName": "Test",
            "displayName": "Test Essai",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    # FIXME On a besoin de rendre prédictible les uuid qu'on génère pendant
    # les tests. On a aussi besoin de définir ce que c'est que l'uuid d'une
    # mailbox, parce que ce n'est pas clair pour l'instant...
    got = response.json()
    assert got["email"] == "address@tutu.net"
    # assert got["uuid"] == something smart here :)

    # Check the password is properly encoded in dovecot database
    imap_user = sql_dovecot.get_user(db_dovecot_session, "address", "tutu.net")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.check_password(got["password"])


def test_alias__creates_and_fetch_an_alias(my_user, db_postfix):
    token = my_user["token"]

    response = client.get(
        "/domains/tutu.net/aliases",
        params={
            "username": "from",
            "domain": "tutu.net",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

    response = client.post(
        "/domains/tutu.net/aliases",
        json={
            "username": "from",
            "domain": "tutu.net",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "from",
        "domain": "tutu.net",
        "destination": "anything@example.com",
    }

    response = client.get(
        "/domains/tutu.net/aliases/",
        params={
            "username": "from",
            "domain": "tutu.net",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "username": "from",
            "domain": "tutu.net",
            "destination": "anything@example.com",
        }
    ]

    response = client.post(
        "/domains/tutu.net/aliases/",
        json={
            "username": "from",
            "domain": "tutu.net",
            "destination": "other@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "from",
        "domain": "tutu.net",
        "destination": "other@example.com",
    }

    response = client.post(
        "/domains/tutu.net/aliases/",
        json={
            "username": "old.chap",
            "domain": "tutu.net",
            "destination": "new.name@company.example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = client.get(
        "/domains/tutu.net/aliases/",
        params={
            "domain": "tutu.net",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(
        "/domains/tutu.net/aliases/",
        params={
            "domain": "tutu.net",
            "username": "from",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert item["domain"] == "tutu.net"
        assert item["username"] == "from"
        assert item["destination"] in ["anything@example.com", "other@example.com"]


def test_permissions(db_api, db_dovecot, my_user, log):
    token = my_user["token"]
    log.info(f"Using token {token}")

    response = client.get(
        "/domains/{domain_name}/mailboxes/toto@tutu.net",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Mailbox not found"}

    response = client.get(
        "/domains/{domain_name}/mailboxes/toto@example.com",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_domains__get_domain_allowed_user(db_api, db_dovecot, my_user, log):
    """When being a domain owner, use can get domains details."""

    token = my_user["token"]
    domain_name = "tutu.net"

    # Get domain
    response = client.get(f"/domains/{domain_name}/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "name": domain_name,
        "features": ["webmail", "mailbox"],
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
    }


def test_domains__get_domain_not_authorized(db_api_session, db_dovecot, my_user):
    """Cannot access details to a domain to which you have no allows."""

    token = my_user["token"]
    domain = sql_api.create_domain(
        db_api_session,
        name="example.com",
        features=["webmail", "mailbox"],
    )
    # Access is not granted to this user

    response = client.get(f"/domains/{domain.name}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authorized."}


def test_domains__get_domain_admin_always_authorized(db_api_session):
    """Admin can access details to all domains."""

    # Create admin user and domain
    sql_api.create_user(db_api_session, name="admin", password="admin_password", is_admin=True)
    response = client.get("/token/", auth=("admin", "admin_password"))
    token = response.json()["access_token"]

    domain = sql_api.create_domain(
        db_api_session,
        name="unused_domain.com",
        features=[],
    )
    # Admin user is not given allows to any domain

    response = client.get(f"/domains/{domain.name}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "name": domain.name,
        "features": domain.features,
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
    }
