import sqlalchemy.orm as orm

from . import models


def get_dovecot_user(db: orm.Session, username: str, domain: str):
    return db.get(models.ImapUser, {"username": username, "domain": domain})

def create_dovecot_user(db: orm.Session, username: str, domain: str, password: str):
    imap_user = models.ImapUser(
        username=username,
        domain=domain,
        active="Y",
        password=f"SHOULD BE ENCODED {password}",
        uid=0,
        gid=0,
        home="",
    )
    try:
        db.add(imap_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
        return None
    db.refresh(imap_user)
    return imap_user
