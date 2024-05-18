import fastapi.testclient
import pytest

from .. import main, routes, sql_api, sql_dovecot

client = fastapi.testclient.TestClient(main.app)


@pytest.fixture(scope="function")
def my_user(db_api, log):
    user = "bidibule"
    domain = "tutu.net"

    res = client.post(
        "/admin/users/", json={"name": user, "password": "toto", "is_admin": False}
    )
    assert res.status_code == 200
    res = client.post(
        "/admin/domains/", json={"name": domain, "features": ["webmail", "mailbox"]}
    )
    assert res.status_code == 200
    res = client.post("/admin/allows/", json={"user": user, "domain": domain})
    assert res.status_code == 200

    res = client.get("/token/", auth=(user, "toto"))
    assert res.status_code == 200
    token = res.json()["access_token"]

    yield {"user": user, "domains": [domain], "token": token}



def test_something(db_api, db_dovecot, my_user, log):
    token = my_user["token"]
    log.info(f"Using token {token}")
    sql_api.set_current_user_name(my_user["user"])

    response = client.get("/mailboxes/toto@tutu.net", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Mailbox not found"}
