import fastapi.testclient

from .. import main

client = fastapi.testclient.TestClient(main.app)


def test_something(db_api, log):
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert response.json() == []
    response = client.post(
        "/admin/users", json={"name": "testing", "password": "toto", "is_admin": False}
    )
    assert response.status_code == 200
    # TODO : Comment piloter la génération des uuid depuis les tests pour les rendre prédictibles ?
    uuid = response.json()["uuid"]
    assert response.json() == {"name": "testing", "uuid": uuid, "is_admin": False}
    response = client.get("/admin/users")
    assert response.status_code == 200
    assert response.json() == [{"name": "testing", "uuid": uuid, "is_admin": False}]
    response = client.post(
        "/admin/users", json={"name": "testing", "password": "titi", "is_admin": False}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}
