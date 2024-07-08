import pytest

import fastapi
import jwt
import datetime

from .. import config


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

    # Si on ne met rien comme en-tête d'autorisation, on ne passe pas
    response = client.get(
        "/domains/example.com/mailboxes/toto",
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Si on ne met pas Bearer comme schema, on ne passe pas
    response = client.get(
        "/domains/example.com/mailboxes/toto",
        headers={"Authorization": f"Pasbearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Si on met un truc qui n'est pas un token, on ne passe pas
    response = client.get(
        "/domains/example.com/mailboxes/toto",
        headers={"Authorization": f"Bearer not-a-valid-token"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_mail",
    ["example.com"],
    indirect=True,
)
def test_weird_tokens(db_api, db_dovecot, log, client, normal_user, domain_mail):
    secret = config.settings["JWT_SECRET"]
    valid_token = normal_user["token"]
    domain_name = domain_mail["name"]

    now = datetime.datetime.now(datetime.timezone.utc)
    delta = datetime.timedelta(minutes=47)
    expire = now + delta
    data = {
        "sub": "not-a-user",
        "exp": expire,
    }
    algo = "HS256"
    token = jwt.encode(data, secret, algo)

    # Avec un token normal d'un user valid, l'appel fonctionne et on a un
    # not found (le domaine n'est pas déclaré)
    response = client.get(
        f"/domains/{domain_name}/mailboxes/toto",
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Si on utilise un token pour un user qui n'existe pas (par exemple,
    # qui a été supprimé après que le token a été fabriqué), on ne passe
    # pas
    response = client.get(
        f"/domains/{domain_name}/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Je fabrique un token expiré, sur un user valide
    expire = now - delta
    data = {
        "sub": normal_user["user"],
        "exp": expire,
    }
    token = jwt.encode(data, secret, algo)
    # Avec ce token, je ne passe pas
    response = client.get(
        f"/domains/{domain_name}/mailboxes/toto",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN


