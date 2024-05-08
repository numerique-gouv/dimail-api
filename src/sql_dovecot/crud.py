import sqlalchemy.orm

from . import models

def get_dovecot_user(db: sqlalchemy.orm.Session, username: str, domain: str):
    return db.get(models.ImapUser, username, domain)
