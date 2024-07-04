import fastapi.testclient
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
def test_permissions(db_api, db_dovecot, log, client, normal_user, domain_mail):
    token = normal_user["token"]
    domain_name = domain_mail["name"]
    log.info(f"Using token {token}")

    response = client.get(
        f"/domains/{domain_name}/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Mailbox not found"}

    response = client.get(
        "/domains/example.com/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403



