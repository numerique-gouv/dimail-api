import fastapi.testclient

from .. import main

client = fastapi.testclient.TestClient(main.app)


def test_something(db_api, log):
    # At the beginning of time, databse is empty, random users accepted and are admins
    response = client.get("/admin/users", auth=("useless", "useless"))
    assert response.status_code == 200
    assert response.json() == []
    response = client.post(
        "/admin/users",
        json={"name": "first_admin", "password": "toto", "is_admin": True},
        auth=("useless", "useless"),
    )
    assert response.status_code == 200
    # TODO : Comment piloter la génération des uuid depuis les tests pour les rendre prédictibles ?
    uuid = response.json()["uuid"]
    assert response.json() == {"name": "first_admin", "uuid": uuid, "is_admin": True}

    # Database is not empty anymore, only admins can do admin requests
    response = client.get("/admin/users", auth=("first_admin", "toto"))
    assert response.status_code == 200
    assert response.json() == [{"name": "first_admin", "uuid": uuid, "is_admin": True}]

    # without auth, we got a 401 error
    response = client.post(
        "/admin/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
    )
    assert response.status_code == 401

    # With auth, but with the wrong password, still fails
    response = client.post(
        "/admin/users",
        json={"name": "testing", "password": "titi", "is_admin": False},
        auth=("first_admin", "wrong_password"),
    )
    assert response.status_code == 401

    # With auth, but creating a user that already exists (and is myself, by the way)
    # will fail
    response = client.post(
        "/admin/users",
        json={"name": "first_admin", "password": "toto", "is_admin": False},
        auth=("first_admin", "toto"),
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User already exists"}
