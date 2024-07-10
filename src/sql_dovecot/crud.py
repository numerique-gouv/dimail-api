import sqlalchemy.orm as orm

from . import models


def get_user(db: orm.Session, username: str, domain: str):
    return db.get(models.ImapUser, {"username": username, "domain": domain})


def get_users(db: orm.Session, domain_name: str):
    return db.query(models.ImapUser).filter(models.ImapUser.domain == domain_name).all()


def create_user(db: orm.Session, username: str, domain: str, password: str):
    imap_user = models.ImapUser(
        username=username,
        domain=domain,
        active="Y",
        password="WILL BE ENCODED",
        uid=0,
        gid=0,
        home="",
    )
    imap_user.set_password(password)
    try:
        db.add(imap_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
        return None
    db.refresh(imap_user)
    return imap_user


def delete_user(db: orm.Session, username: str, domain: str):
    user = get_user(db, username, domain)
    if user is not None:
        db.delete(user)
        db.commit()
    return user
