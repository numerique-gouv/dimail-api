import logging
from .. import sql_dovecot

def test_useless(db_dovecot_session):

    imap_user = sql_dovecot.get_dovecot_user(db_dovecot_session, "toto", "example.com")
    assert imap_user is None

    imap_user = sql_dovecot.create_dovecot_user(db_dovecot_session, "toto", "example.com", "secret")
    assert isinstance(imap_user, sql_dovecot.ImapUser)

    imap_user = sql_dovecot.get_dovecot_user(db_dovecot_session, "toto", "example.com")
    assert isinstance(imap_user, sql_dovecot.ImapUser)
    assert imap_user.username == "toto"
    assert imap_user.domain == "example.com"
    assert imap_user.check_password("secret")
    log = logging.getLogger(__name__)
    log.info(f"Encrypted: {imap_user.password}")
