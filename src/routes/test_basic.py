import fastapi.testclient
import pytest

from .. import main

client = fastapi.testclient.TestClient(main.app)


@pytest.fixture(scope="function")
def my_user(db_api, log):
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
        json={"name": domain, "features": ["webmail", "mailbox"]},
        auth=("admin", "admin"),
    )
    assert res.status_code == 200

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
