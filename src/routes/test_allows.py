import fastapi.testclient
import pytest

@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_web",
    ["example.com:dimail"],
    indirect=True,
)
def test_allow__create_errors(client, log, admin, normal_user, domain_web):
    auth=(admin["user"], admin["password"])

    # If the user does not exist -> not found
    response = client.post(
        "/allows/",
        json={"domain": "example.com", "user": "unknown"},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # If the domain does not exist -> not found
    response = client.post(
        "/allows/",
        json={"domain": "unknown.com", "user": normal_user["user"]},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # If the allows already exists -> conflict
    response = client.post(
        "/allows/",
        json={"domain": "example.com", "user": normal_user["user"]},
        auth=auth,
    )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT
