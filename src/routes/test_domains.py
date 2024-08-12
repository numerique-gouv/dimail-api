# ruff: noqa: E712
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
    no_test = {"code": "no_test", "detail": "Did not check yet"}
    assert response.json() == {
        "name": domain_name,
        "valid": False,
        "state": "new",
        "features": ["mailbox", "webmail"],
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
        "domain_exist": {"ok": False, "errors": [no_test]},
        "mx": {"ok": False, "errors": [no_test]},
        "cname_imap": {"ok": False, "errors": [no_test]},
        "cname_smtp": {"ok": False, "errors": [no_test]},
        "cname_webmail": {"ok": False, "errors": [no_test]},
        "spf": {"ok": False, "errors": [no_test]},
        "dkim": {"ok": False, "errors": [no_test]},
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
    no_test = {"code": "no_test", "detail": "Did not check yet"}
    assert response.json() == {
        "name": domain_name,
        "valid": False,
        "state": "new",
        "features": domain_features,
        "mailbox_domain": None,
        "webmail_domain": None,
        "imap_domains": None,
        "smtp_domains": None,
        "context_name": None,
        "domain_exist": {"ok": False, "errors": [no_test]},
        "mx": {"ok": False, "errors": [no_test]},
        "cname_imap": {"ok": False, "errors": [no_test]},
        "cname_smtp": {"ok": False, "errors": [no_test]},
        "cname_webmail": {"ok": False, "errors": [no_test]},
        "spf": {"ok": False, "errors": [no_test]},
        "dkim": {"ok": False, "errors": [no_test]},
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

@pytest.mark.parametrize(
    "normal_user",
    ["bidibule:toto"],
    indirect=True,
)
@pytest.mark.parametrize(
    "domain_web",
    ["example.com:dimail"],
    indirect=True
)
def test_domains_check_domain(db_api_session, admin, log, client, normal_user, domain_web):
    auth=(admin["user"], admin["password"])

    domain_name = domain_web["name"]
    response = client.get(f"/domains/{domain_name}/check", auth=auth)
    assert response.status_code == fastapi.status.HTTP_200_OK
    infos = response.json()
    assert infos["name"] == "example.com"
    assert infos["state"] == "broken"
    assert infos["valid"] == False
    for key in [ "domain_exist", "mx", "cname_imap", "cname_smtp", "cname_webmail", "spf", "dkim" ]:
        assert key in infos
        assert "ok" in infos[key]
        assert "errors" in infos[key]
        if infos[key]["ok"]:
            assert len(infos[key]["errors"]) == 0
        else:
            assert len(infos[key]["errors"]) > 0
    assert infos["domain_exist"]["ok"] is True
    assert infos["mx"]["ok"] is False
    assert len(infos["mx"]["errors"]) == 1
    assert infos["mx"]["errors"][0]["code"] == "wrong_mx"

    assert infos["cname_imap"]["ok"] is False
    assert len(infos["cname_imap"]["errors"]) == 1
    assert infos["cname_imap"]["errors"][0]["code"] == "no_cname_imap"

    assert infos["cname_smtp"]["ok"] is False
    assert len(infos["cname_smtp"]["errors"]) == 1
    assert infos["cname_smtp"]["errors"][0]["code"] == "no_cname_smtp"

    assert infos["cname_webmail"]["ok"] is False
    assert len(infos["cname_webmail"]["errors"]) == 1
    assert infos["cname_webmail"]["errors"][0]["code"] == "no_cname_webmail"

    assert infos["spf"]["ok"] is False
    assert infos["dkim"]["ok"] is False
    assert len(infos["dkim"]["errors"]) == 1
    assert infos["dkim"]["errors"][0]["code"] == "no_dkim"

