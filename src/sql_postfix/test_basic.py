import pytest

from . import database
from .. import sql_postfix


def test_database():
    database.maker = None
    with pytest.raises(Exception) as e:
        database.get_maker()
    assert "Please init the postfix database by giving me an url..." in str(e.value)

    database.init_db("sqlite:///:memory:")

    maker = database.get_maker()
    assert maker is not None

def test_alias__create_and_get_an_alias(db_postfix_session):
    """Proves that we can create an alias in postfix db, and fetch it."""
    alias = sql_postfix.get_alias(
        db_postfix_session, "from@example.com", "to@example.com"
    )
    assert alias is None

    # On vérifie que si une valeur est idiote on ne peut pas creer d'alias
    alias = sql_postfix.create_alias(db_postfix_session, None, "from", "to@example.com")
    assert alias is None

    alias = sql_postfix.create_alias(db_postfix_session, "example.com", None, "to@example.com")
    assert alias is None

    alias = sql_postfix.create_alias(db_postfix_session, None, "from", None)
    assert alias is None

    alias = sql_postfix.create_alias(
        db_postfix_session, "example.com", "from", "to@example.com"
    )
    assert isinstance(alias, sql_postfix.Alias)

    alias = sql_postfix.get_alias(
        db_postfix_session, "from@example.com", "to@example.com"
    )
    assert isinstance(alias, sql_postfix.Alias)
    assert alias.alias == "from@example.com"
    assert alias.destination == "to@example.com"
    assert alias.domain == "example.com"

    alias = sql_postfix.create_alias(
        db_postfix_session, "example.com", "from", "other@gmail.com"
    )
    assert isinstance(alias, sql_postfix.Alias)

    count = sql_postfix.delete_alias(
        db_postfix_session, "from@example.com", "to@example.com"
    )
    assert count == 1

    alias = sql_postfix.create_alias(
        db_postfix_session, "example.com", "from", "something@gmail.com"
    )
    assert isinstance(alias, sql_postfix.Alias)

    count = sql_postfix.delete_aliases_by_name(
        db_postfix_session, "from@example.com"
    )
    assert count == 2

    count = sql_postfix.delete_aliases_by_name(
        db_postfix_session, "from@example.com"
    )
    assert count == 0


def test__mailbox_domain(db_postfix_session):
    """Proves we can create, fetch and delete mailbox domains in postfix db"""
    dom = sql_postfix.get_mailbox_domain(db_postfix_session, "example.com")
    assert dom is None

    # On vérifie qu'une valeur None n'est pas admise, ni pour domain ni pour mailbox_domain
    dom = sql_postfix.create_mailbox_domain(db_postfix_session, None, "target.domain.fr")
    assert dom is None

    dom = sql_postfix.create_mailbox_domain(db_postfix_session, "example.com", None)
    assert dom is None

    # On vérifie qu'on peut faire une création normale
    dom = sql_postfix.create_mailbox_domain(db_postfix_session, "example.com", "target.domain.fr")
    assert isinstance(dom, sql_postfix.MailboxDomain)

    dom = sql_postfix.get_mailbox_domain(db_postfix_session, "example.com")
    assert isinstance(dom, sql_postfix.MailboxDomain)
    assert dom.domain == "example.com"
    assert dom.mailbox_domain == "target.domain.fr"

    # On vérifie qu'on ne peut pas créer un deuxième mailbox_domain pour le même domain
    dom = sql_postfix.create_mailbox_domain(db_postfix_session, "example.com", "autre.domain.fr")
    assert dom is None

    # On vérifie qu'on peut supprimer le mailbox_domain qu'on vient de créer
    count = sql_postfix.delete_mailbox_domain(db_postfix_session, "example.com")
    assert count == 1

    # On vérifie qu'on ne peut pas supprimer un mailbox_domain qui n'existe pas
    count = sql_postfix.delete_mailbox_domain(db_postfix_session, "existepas.fr")
    assert count == 0


def test__alias_domain(db_postfix_session):
    """Proves we can create, fetch and delete alias domains in postfix db"""
    dom = sql_postfix.get_alias_domain(db_postfix_session, "example.com")
    assert dom is None

    # On vérifie qu'une valeur None n'est pas admis, ni pour domain ni pour alias_domain
    dom = sql_postfix.create_alias_domain(db_postfix_session, None, "target.domain.fr")
    assert dom is None

    dom = sql_postfix.create_alias_domain(db_postfix_session, "example.com", None)
    assert dom is None

    # On vérifie qu'on peut faire une création normale
    dom = sql_postfix.create_alias_domain(db_postfix_session, "example.com", "target.domain.fr")
    assert isinstance(dom, sql_postfix.AliasDomain)

    dom = sql_postfix.get_alias_domain(db_postfix_session, "example.com")
    assert isinstance(dom, sql_postfix.AliasDomain)
    assert dom.domain == "example.com"
    assert dom.alias_domain == "target.domain.fr"

    # On vérifie qu'on ne peut pas créer un deuxième alias_domain pour le même domain
    dom = sql_postfix.create_alias_domain(db_postfix_session, "example.com", "autre.domain.fr")
    assert dom is None

    # On vérifie qu'on peut supprimer le alias_domain qu'on vient de créer
    count = sql_postfix.delete_alias_domain(db_postfix_session, "example.com")
    assert count == 1

    # On vérifie qu'on ne peut pas supprimer un alias_domain qui n'existe pas
    count = sql_postfix.delete_alias_domain(db_postfix_session, "existepas.fr")
    assert count == 0

