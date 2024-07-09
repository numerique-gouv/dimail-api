import fastapi.testclient
import pytest

from .. import sql_dovecot


# Dans la première serie de tests, on travaille sur un domaine avec le webmail.

@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "virgin_user",
    ["bidi:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_web",
    ["tutu.net:dimail"],
    indirect=True,
)
def test_with_webmail(client, normal_user, virgin_user, domain_web, db_dovecot_session, admin_token):
    token = normal_user["token"]
    virgin_token = virgin_user["token"]
    admin_token = admin_token["token"]
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

    # Le virgin_user ne peut pas créer de mailbox -> forbidden
    response = client.post(
        f"/domains/{domain_name}/mailboxes/address",
        json={
            "surName": "Essai",
            "givenName": "Test",
            "displayName": "Test Essai",
        },
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

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

    # On modifie la mailbox
    response = client.patch(
        f"/domains/{domain_name}/mailboxes/address",
        json={
            "givenName": "AutreTest",
            "surName": "EssaiNouveau",
            "displayName": "Joli nom affichable",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "type": "mailbox",
        "status": "ok",
        "email": f"address@{domain_name}",
        "surName": "EssaiNouveau",
        "givenName": "AutreTest",
        "displayName": "Joli nom affichable",
    }

    # Si on patch sur un domaine qui n'existe pas -> not found
    # Il faut etre admin pour pouvoir essayer de toucher un domaine qui
    # n'existe pas, les gens normaux auront un permisison denied.
    response = client.patch(
        f"/domains/pas-un-domaine/mailboxes/hop",
        json={},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Si on patch sur un domaine où on n'a pas les droits (qui n'existe pas,
    # dans notre cas) -> forbidden
    response = client.patch(
        f"/domains/pas-un-domaine/mailboxes/hop",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Si on patch sur une mailbox qui n'existe pas -> not found
    response = client.patch(
        f"/domains/{domain_name}/mailboxes/pas-une-boite",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Si on veut modifier le domaine pour un domaine qui n'existe pas -> not found
    # Il faut être admin pour pouvoir essayer de toucher un domaine qui
    # n'existe pas, les gens normaux auront un permission denied.
    response = client.patch(
        f"/domains/{domain_name}/mailboxes/pas-une-boite",
        json={
            "domain": "pas-un-domaine",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

    # Si on veut modifier le domaine pour un domaine où on n'a pas les
    # droits (ici, un domaine qui n'existe pas) -> forbidden
    response = client.patch(
        f"/domains/{domain_name}/mailboxes/pas-une-boite",
        json={
            "domain": "pas-un-domaine",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

    # Le virgin_user ne peut pas GET de mailbox -> forbidden
    response = client.get(
        f"/domains/{domain_name}/mailboxes",
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

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
    "virgin_user",
    ["bidi:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_mail",
    ["tutu.org"],
    indirect=True,
)
def test_without_webmail(client, normal_user, virgin_user, domain_mail, db_dovecot_session):
    token = normal_user["token"]
    virgin_token = virgin_user["token"]
    domain_name = domain_mail["name"]

    # Le virgin_user ne peut pas GET de mailbox -> forbidden
    response = client.get(
        f"/domains/{domain_name}/mailboxes/address",
        headers={"Authorization": f"Bearer {virgin_token}"},
    )
    assert response.status_code == fastapi.status.HTTP_403_FORBIDDEN

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


