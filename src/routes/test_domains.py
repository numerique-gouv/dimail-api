import fastapi.testclient
import pytest

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
def test_domains__get_domain_allowed_user(db_api, db_dovecot, log, client, normal_user, domain_web):
    """When being a domain owner, use can get domains details."""

    token = normal_user["token"]
    domain_name = domain_web["name"]

    # Get domain
    response = client.get(f"/domains/{domain_name}/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "name": domain_name,
        "features": ["mailbox", "webmail"],
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
    }


@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain",
    ["example.com"],
    indirect=True,
)
def test_domains__get_domain_not_authorized(db_dovecot, normal_user, domain, client):
    """Cannot access details to a domain to which you have no allows."""

    token = normal_user["token"]
    domain_name = domain["name"]
    # Access is not granted to this user
    response = client.get(f"/domains/{domain_name}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authorized."}


@pytest.mark.parametrize(
    "domain",
    ["example.com"],
    indirect=True,
)
def test_domains__get_domain_admin_always_authorized(db_api_session, domain, admin, client):
    """Admin can access details to all domains."""
    domain_name = domain["name"]
    domain_features = domain["features"]

    # Get a token for the admin user
    response = client.get("/token/", auth=(admin["user"], admin["password"]))
    token = response.json()["access_token"]

    # Admin user is not given allows to any domain, but still can get
    # access to the details of the domain
    response = client.get(f"/domains/{domain_name}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == fastapi.status.HTTP_200_OK
    assert response.json() == {
        "name": domain_name,
        "features": domain_features,
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
    }

    # If the domain does not exist -> not found
    response = client.get("/domains/unknown_domain/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == fastapi.status.HTTP_404_NOT_FOUND

@pytest.mark.parametrize(
    "domain",
    ["example.com"],
    indirect=True,
)
def test_domains_create_failed(db_api_session, admin, log, client, domain):
    auth=(admin["user"], admin["password"])

    # A domain with the feature 'webmail' MUST have a context_name
    response = client.post("/domains/",
                json={"name": "new.com", "features": ["mailbox", "webmail"], "context_name": None},
                auth=auth
        )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT

    # If the domain already exists -> conflict
    response = client.post("/domains/",
                json={
                    "name": "example.com",
                    "features": ["mailbox", "webmail"],
                    "context_name": "dimail"
                },
                auth=auth
           )
    assert response.status_code == fastapi.status.HTTP_409_CONFLICT

