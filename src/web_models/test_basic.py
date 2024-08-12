import pytest

from .. import (
    oxcli,
    sql_dovecot,
    sql_postfix,
    web_models
)

def test_web_model_mailbox():
    with pytest.raises(Exception) as e:
        user = web_models.Mailbox.from_both_users(None, None, False)
    assert "At least" in str(e.value)

    ox_cluster = oxcli.OxCluster()
    ox_context = oxcli.OxContext(
        cid=1,
        name="context",
        domains=(),
        cluster=ox_cluster,
    )
    ox_user = oxcli.OxUser(
        uid=1,
        username="toto",
        givenName="Prénom",
        surName="Nom",
        displayName="Prénom Nom",
        email="toto@domain.fr",
        ctx=ox_context,
    )
    db_user = sql_dovecot.ImapUser(
        username = "toto",
        domain = "domain.com",
        password = "invalid",
        home = "useless",
        uid = 0,
        gid = 0,
        active = "Y",
    )
    assert db_user.email() == "toto@domain.com"
    assert ox_user.email == "toto@domain.fr"
    with pytest.raises(Exception) as e:
        user = web_models.Mailbox.from_both_users(ox_user, db_user, True)
        assert user is None
    assert "the same" in str(e.value)

    # Maintenant, nos deux users sont cohérents
    db_user.domain = "domain.fr"

    # Si on dit qu'on a du webmail, le status est "ok"
    user = web_models.Mailbox.from_both_users(ox_user, db_user, True)
    assert user.status == "ok"

    # Si on dit qu'on n'a pas de webmail, mais qu'on a un ox_user, "broken"
    user = web_models.Mailbox.from_both_users(ox_user, db_user, False)
    assert user.status == "broken"

    # Si on dit qu'on a du webmail, mais pas de ox_user, "broken"
    user = web_models.Mailbox.from_both_users(None, db_user, True)
    assert user.status == "broken"

    # Si pas de webmail et pas de ox_user, "ok"
    user = web_models.Mailbox.from_both_users(None, db_user, False)
    assert user.status == "ok"

def test_alias_webmodel():
    username = "toto"
    domain = "domain.com"
    destination = "destination"

    postfix_alias = sql_postfix.Alias(
        alias=f"{username}@{domain}",
        domain="domain",
        destination=destination,
    )

    # On crée un alias à partir de la base de données
    # On vérifie que l'alias n'as pas été créé
    # Car le domaine est incorrect
    with pytest.raises(Exception) as e:
        web_models.Alias.from_db(postfix_alias)
    assert "The alias in database" in str(e.value)

    # On corrige le domaine
    postfix_alias.domain = domain

    # On crée l'alias
    alias = web_models.Alias.from_db(postfix_alias)

    assert alias.username == username
    assert alias.domain == domain
    assert alias.destination == destination

