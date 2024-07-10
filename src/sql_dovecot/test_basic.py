from .. import sql_dovecot


def test_imap__create_and_get_a_user(db_dovecot_session):
    """Proves that we can create a user in dovecot db, fetch it, and checks its password."""
    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert imap_user is None

    imap_user = sql_dovecot.create_user(
        db_dovecot_session, "toto", "example.com", "secret"
    )
    assert isinstance(imap_user, sql_dovecot.ImapUser)

    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.username == "toto"
    assert imap_user.domain == "example.com"
    assert imap_user.check_password("secret")

    # Quand on supprime le user, on le récupère tel qu'il était avant suppression
    imap_user = sql_dovecot.delete_user(db_dovecot_session, "toto", "example.com")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.username == "toto"
    assert imap_user.domain == "example.com"

    # Après qu'on l'a supprimé, le user n'existe plus.
    imap_user = sql_dovecot.get_user(db_dovecot_session, "toto", "example.com")
    assert imap_user is None
