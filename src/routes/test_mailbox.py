import fastapi.testclient
import pytest

from .. import sql_dovecot


@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_web",
    ["tutu.net:dimail"],
    indirect=True,
)
def test_create_mailbox(client, normal_user, domain_web, db_dovecot_session):
    token = normal_user["token"]
    domain_name = domain_web["name"]

    response = client.post(
        f"/domains/{domain_name}/mailboxes/address",
        json={
            "surName": "Essai",
            "givenName": "Test",
            "displayName": "Test Essai",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    # FIXME On a besoin de rendre prédictible les uuid qu'on génère pendant
    # les tests. On a aussi besoin de définir ce que c'est que l'uuid d'une
    # mailbox, parce que ce n'est pas clair pour l'instant...
    got = response.json()
    assert got["email"] == "address@tutu.net"
    # assert got["uuid"] == something smart here :)

    # Check the password is properly encoded in dovecot database
    imap_user = sql_dovecot.get_user(db_dovecot_session, "address", "tutu.net")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.check_password(got["password"])


