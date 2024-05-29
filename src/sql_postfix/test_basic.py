from .. import sql_postfix

def test_alias__create_and_get_an_alias(db_postfix_session):
    """Proves that we can create an alias in postfix db, and fetch it."""
    alias = sql_postfix.get_alias(db_postfix_session, "from@example.com", "to@example.com")
    assert alias is None

    alias = sql_postfix.create_alias(db_postfix_session, "example.com", "from", "to@example.com")
    assert isinstance(alias, sql_postfix.PostfixAlias)

    alias = sql_postfix.get_alias(db_postfix_session, "from@example.com", "to@example.com")
    assert isinstance(alias, sql_postfix.PostfixAlias)
    assert alias.alias == "from@example.com"
    assert alias.destination == "to@example.com"
    assert alias.domain == "example.com"
