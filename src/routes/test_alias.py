import pytest

@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_mail",
    ["tutu.net"],
    indirect=True,
)
def test_alias__creates_and_fetch_an_alias(client, normal_user, domain_mail, db_postfix):
    token = normal_user["token"]
    domain_name = domain_mail["name"]

    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "from",
        "domain": domain_name,
        "destination": "anything@example.com",
    }

    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == [
        {
            "username": "from",
            "domain": domain_name,
            "destination": "anything@example.com",
        }
    ]

    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "other@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "username": "from",
        "domain": domain_name,
        "destination": "other@example.com",
    }

    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "old.chap",
            "destination": "new.name@company.example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 2
    for item in response.json():
        assert item["domain"] == domain_name
        assert item["username"] == "from"
        assert item["destination"] in ["anything@example.com", "other@example.com"]


