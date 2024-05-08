# import fastapi
import fastapi.testclient

from .. import main, sql_api

client = fastapi.testclient.TestClient(main.app)


def test_something(db_api_maker, log):
    main.app.dependency_overrides[sql_api.get_api_db] = db_api_maker
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert response.json() == []
    response = client.post("/admin/users", json={"name": "testing", "is_admin": False})
    assert response.status_code == 200
    assert response.json() == {"name": "testing", "is_admin": False}
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert response.json() == [{"name": "testing", "is_admin": False}]
    response = client.post("/admin/users", json={"name": "testing", "is_admin": False})
    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}
