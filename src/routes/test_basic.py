import fastapi.testclient
import pytest

from .. import main, sql_dovecot

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
    assert res.status_code == 200

    # Now, we can create our non-admin user
    res = client.post(
        "/admin/users/",
        json={"name": user, "password": "toto", "is_admin": False},
        auth=("admin", "admin"),
    )
    assert res.status_code == 200

    res = client.post(
        "/admin/domains/",
        json={
            "name": domain,
            "features": ["webmail", "mailbox"],
            "context_name": "dimail",
        },
        auth=("admin", "admin"),
    )
    assert res.status_code == 200

    ctx = ox_cluster.get_context_by_name("dimail")
    assert domain in ctx.domains

    res = client.post(
        "/admin/allows/",
        json={"user": user, "domain": domain},
        auth=("admin", "admin"),
    )
    assert res.status_code == 200

    res = client.get("/token/", auth=(user, "toto"))
    assert res.status_code == 200

    token = res.json()["access_token"]
    yield {"user": user, "domains": [domain], "token": token}


def test_create_mailbox(ox_cluster, my_user, db_dovecot_session):
    token = my_user["token"]

    response = client.post(
        "/mailboxes",
        json={
            "email": "address@tutu.net",
            "surName": "Essai",
            "givenName": "Test",
            "displayName": "Test Essai",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    # FIXME On a besoin de rendre prédictible les uuid qu'on génère pendant
    # les tests. On a aussi besoin de définir ce que c'est que l'uuid d'une
    # mailbox, parce que ce n'est pas clair pour l'instant...
    got = response.json()
    assert got["email"] == "address@tutu.net"
    # assert got["uuid"] == something smart here :)

    # Check the password is properly encoded in dovecot database
    imap_user = sql_dovecot.get_dovecot_user(db_dovecot_session, "address", "tutu.net")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.check_password(got["password"])


def test_something(db_api, db_dovecot, my_user, log):
    token = my_user["token"]
    log.info(f"Using token {token}")

    response = client.get(
        "/mailboxes/toto@tutu.net", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Mailbox not found"}

    response = client.get(
        "/mailboxes/toto@example.com", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
