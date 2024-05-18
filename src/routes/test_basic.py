import fastapi.testclient
import pytest

from .. import main, routes, sql_api, sql_dovecot

client = fastapi.testclient.TestClient(main.app)


@pytest.fixture(scope="function")
def my_user(db_api_maker, log):
    main.app.dependency_overrides[sql_api.get_api_db] = db_api_maker

    user = "bidibule"
    domain = "tutu.net"

    res = client.post(
        "/admin/users",
        json={
            "name": user,
            "password": "toto",
            "is_admin": False
        }
    )
    assert res.status_code == 200
    res = client.post(
        "/admin/domains",
        json={
            "name": domain,
            "features": ["webmail", "mailbox"]
        }
    )
    assert res.status_code == 200
    client.post(
        "/admin/allows",
        json={
            "user": user,
            "domain": domain
        }
    )
    assert res.status_code == 200

    yield {"user": user, "domains": [domain]}


@pytest.fixture(scope="function")
def get_creds(db_api_maker, log):
    yield lambda: sql_api.get_creds(db_api_maker())


def test_something(db_dovecot_maker, get_creds, my_user, log):
    main.app.dependency_overrides[sql_dovecot.get_dovecot_db] = db_dovecot_maker
    main.app.dependency_overrides[routes.get_creds] = get_creds

    sql_api.set_current_user_name(my_user["user"])

    response = client.get("/mailboxes/toto@tutu.net")
    assert response.status_code == 404
    assert response.json() == {"detail": "Mailbox not found"}
