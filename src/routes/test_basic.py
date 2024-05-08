import pytest
import fastapi.testclient
from .. import main
from .. import sql_api
from .. import sql_dovecot
from .. import creds

client = fastapi.testclient.TestClient(main.app)

@pytest.fixture(scope="function")
def my_user(db_api_maker, log):
    main.app.dependency_overrides[sql_api.get_api_db] = db_api_maker

    client.post("/admin/users", json={"name": "bidibule", "is_admin": False})
    client.post("/admin/domains", json={"name": "tutu.net", "features": ["webmail", "mailbox"]})
    client.post("/admin/allows", json={"user": "bidibule", "domain": "tutu.net"})

def test_something(db_dovecot_maker, my_user, log):
    main.app.dependency_overrides[sql_dovecot.get_dovecot_db] = db_dovecot_maker

    creds.user_name = "bidibule"

    response = client.get('/mailboxes/toto@tutunet')
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}

#     response = client.get('/admin/users')
#     assert response.status_code == 200
#     assert response.json() == []
#     response = client.post('/admin/users', json={"name": "testing", "is_admin": False})
#     assert response.status_code == 200
#     assert response.json() == {"name": "testing", "is_admin": False}
#     response = client.get('/admin/users')
#     assert response.status_code == 200
#     assert response.json() == [{"name": "testing", "is_admin": False}]
#     response = client.post('/admin/users', json={"name": "testing", "is_admin": False})
#     assert response.status_code == 200
#     assert response.json() == ["plop"]
