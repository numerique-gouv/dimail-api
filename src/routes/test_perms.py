import pytest
import fastapi

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

    # Si un utilisateur normal (pas un admin) demande la creation d'un domaine,
    # il échoue -> forbidden
    response = client.post(
        f"/domains/",
        json = {
            "name": "new.com",
            "features": ["mailbox"]
        },
        auth=(normal_user["user"], normal_user["password"])
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Si un utilisateur qui n'existe pas essaye de faire quelque chose, il
    # echoue -> forbidden
    response = client.get(
        f"/token",
        auth=("unknown", "mot de passe idiot"),
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Sur notre domaine, un user normal a le droit (mais la mailbox n'existe pas)
    # donc 404.
    response = client.get(
        f"/domains/{domain_name}/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Mailbox not found"}

    # Notre utilisateur n'a pas le droit sur le domaine example.com (qui n'existe pas,
    # mais ce n'est pas le sujet testé ici)
    response = client.get(
        "/domains/example.com/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN



