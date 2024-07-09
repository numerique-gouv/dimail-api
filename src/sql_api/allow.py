import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def get_allows(db: orm.Session, user: str = "", domain: str = ""):
    query = db.query(models.DBAllowed)
    if user != "":
        query = query.filter_by(user=user)
    if domain != "":
        query = query.filter_by(domain=domain)
    return query.all()


def get_allowed(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    return db.get(models.DBAllowed, {"domain": domain, "user": user})
    return db.query(models.DBAllowed).filter_by(domain=domain, user=user).first()


def allow_domain_for_user(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Says the domain is allowed for the user. The user can manage mailboxes and
    aliases on that domain."""
    db_allowed = models.DBAllowed(domain=domain, user=user)
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed


def deny_domain_for_user(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Says the domain is denied (not allowed anymore) for the user. The user will
    not anymore be able to manage the aliases and the mailboxes on that domain."""
    db_allowed = get_allowed(db, user, domain)
    if db_allowed is not None:
        db.delete(db_allowed)
        db.commit()
    return db_allowed


def delete_allows_by_user(db: orm.Session, user: str) -> int:
    """Delete all the allows for this user."""
    res = db.execute(sa.delete(models.DBAllowed).where(models.DBAllowed.user == user))
    db.commit()
    return res.rowcount
