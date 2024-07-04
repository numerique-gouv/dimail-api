import fastapi.testclient
import pytest

from .. import sql_dovecot


# Dans la première serie de tests, on travaille sur un domaine avec le webmail.

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
def test_with_webmail(client, normal_user, domain_web, db_dovecot_session):
    token = normal_user["token"]
    domain_name = domain_web["name"]

    # On obtient un 404 sur une mailbox qui n'existe pas
    response = client.get(
        f"/domains/{domain_name}/mailboxes/address",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # On get toutes les boites du domaine, on doit remonter une liste avec
    # une seule boite, le context admin, qui doit être broken (il n'existe
    # pas en imap)
    response = client.get(
        f"/domains/{domain_name}/mailboxes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    json = response.json()
    assert len(json) == 1
    assert json[0]["email"] == f"oxadmin@{domain_name}"
    assert json[0]["status"] == "broken"

    # On crée la mailbox qui n'existait pas à la ligne précédente
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
    assert got["email"] == f"address@{domain_name}"
    # assert got["uuid"] == something smart here :)

    # Check the password is properly encoded in dovecot database
    imap_user = sql_dovecot.get_user(db_dovecot_session, "address", domain_name)
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.check_password(got["password"])

    # On refait un GET sur la boîte qu'on vient de créer
    response = client.get(
        f"/domains/{domain_name}/mailboxes/address",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "type": "mailbox",
        "status": "ok",
        "email": f"address@{domain_name}",
        "surName": "Essai",
        "givenName": "Test",
        "displayName": "Test Essai",
    }

    # On get toutes les boites du domaine, on doit remonter notre
    # boite neuve
    response = client.get(
        f"/domains/{domain_name}/mailboxes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    json = response.json()
    assert len(json) == 2
    emails = [ json[0]["email"], json[1]["email"] ]
    assert f"address@{domain_name}" in emails



@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_mail",
    ["tutu.org"],
    indirect=True,
)
def test_without_webmail(client, normal_user, domain_mail, db_dovecot_session):
    token = normal_user["token"]
    domain_name = domain_mail["name"]

    # On obtient un 404 sur une mailbox qui n'existe pas
    response = client.get(
        f"/domains/{domain_name}/mailboxes/address",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # On get toutes les boites du domaine, on doit remonter une liste vide
    # (pas de webmail, donc pas de boite oxadmin, puisque pas de ox)
    response = client.get(
        f"/domains/{domain_name}/mailboxes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    json = response.json()
    assert len(json) == 0

    # On crée la mailbox qui n'existait pas à la ligne précédente
    response = client.post(
        f"/domains/{domain_name}/mailboxes/address",
        json={
            "givenName": "",
            "surName": "",
            "displayName": "",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_201_CREATED
    # FIXME On a besoin de rendre prédictible les uuid qu'on génère pendant
    # les tests. On a aussi besoin de définir ce que c'est que l'uuid d'une
    # mailbox, parce que ce n'est pas clair pour l'instant...
    got = response.json()
    assert got["email"] == f"address@{domain_name}"
    # assert got["uuid"] == something smart here :)

    # Check the password is properly encoded in dovecot database
    imap_user = sql_dovecot.get_user(db_dovecot_session, "address", domain_name)
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.check_password(got["password"])

    # On refait un GET sur la boîte qu'on vient de créer
    response = client.get(
        f"/domains/{domain_name}/mailboxes/address",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "type": "mailbox",
        "status": "broken",
        "email": f"address@{domain_name}",
        "surName": None,
        "givenName": None,
        "displayName": None,
    }

    # On get toutes les boites du domaine, on doit remonter notre
    # boite neuve
    response = client.get(
        f"/domains/{domain_name}/mailboxes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    json = response.json()
    assert len(json) == 1
    assert json[0]["email"] == f"address@{domain_name}"


