import pytest

import fastapi

@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "virgin_user",
    ["virgin:empty"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_mail",
    ["tutu.net"],
    indirect=True,
)
def test_alias__creates_and_fetch_an_alias(
        client,
        normal_user,
        virgin_user,
        domain_mail,
        db_postfix
    ):
    token = normal_user["token"]
    virgin_token = virgin_user["token"]
    domain_name = domain_mail["name"]

    # The alias does not exist
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # The virgin user cannot create the alias
    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # We create the alias
    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "username": "from",
        "domain": domain_name,
        "destination": "anything@example.com",
    }

    # We try to create the alias again (should fail, duplicate)
    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT

    # Permission denied for virgin_user when he tries to GET
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # One cannot GET an alias with destination and no user_name
    # (that would mean listing all the aliases which contains "destination",
    # which is not a reasonable request)
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_412_PRECONDITION_FAILED

    # We fetch the alias
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
            "destination": "anything@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == [
        {
            "username": "from",
            "domain": domain_name,
            "destination": "anything@example.com",
        }
    ]

    # We add a new destination to the alias
    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "from",
            "destination": "other@example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "username": "from",
        "domain": domain_name,
        "destination": "other@example.com",
    }

    # We create another alia
    response = client.post(
        f"/domains/{domain_name}/aliases/",
        json={
            "user_name": "old.chap",
            "destination": "new.name@company.example.com",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK

    # We fetch all the aliases for the domain, we have 2 aliases,
    # one being for 2 destinations (so, 3 lines)
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert len(response.json()) == 3

    # We fetch the alias having 2 destinations and check the destinations
    # are correct
    response = client.get(
        f"/domains/{domain_name}/aliases/",
        params={
            "user_name": "from",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert len(response.json()) == 2
    for item in response.json():
        assert item["domain"] == domain_name
        assert item["username"] == "from"
        assert item["destination"] in ["anything@example.com", "other@example.com"]

    # We remove a destination from an alias, first from an alias that
    # does not exist
    response = client.delete(
        f"/domains/{domain_name}/aliases/pas-un-alias/destination",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # We remove all the destinations from an alias, for an alias that
    # does not exist
    response = client.delete(
        f"/domains/{domain_name}/aliases/pas-un-alias/all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # We remove a destination from an alias which exists
    response = client.delete(
        f"/domains/{domain_name}/aliases/old.chap/new.name@company.example.com",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT

    # We remove all the destinations from an alias which exists
    response = client.delete(
        f"/domains/{domain_name}/aliases/from/all",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_204_NO_CONTENT

    # We check that the virgin user cannot delete an alias
    response = client.delete(
        f"/domains/{domain_name}/aliases/from/all",
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

