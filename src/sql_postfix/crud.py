import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def get_alias(db: orm.Session, alias: str, destination: str):
    return db.get(models.Alias, {"alias": alias, "destination": destination})


def get_aliases_by_domain(db: orm.Session, domain: str):
    return (
        db.query(models.Alias).filter(models.Alias.domain == domain).all()
    )


def get_aliases_by_name(db: orm.Session, name: str):
    return db.query(models.Alias).filter(models.Alias.alias == name).all()


def create_alias(
    db: orm.Session, domain: str, username: str, destination: str
) -> models.Alias:
    try:
        alias = username + "@" + domain
        db_alias = models.Alias(
            alias=alias,
            domain=domain,
            destination=destination,
        )
        db.add(db_alias)
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_alias)
    return db_alias


def delete_alias(db: orm.Session, alias: str, destination: str) -> int:
    db_alias = get_alias(db, alias, destination)
    if db_alias is not None:
        db.delete(db_alias)
        db.commit()
        return 1
    return 0


def delete_aliases_by_name(db: orm.Session, name: str):
    res = db.execute(sa.delete(models.Alias).where(models.Alias.alias == name))
    db.commit()
    return res.rowcount


def get_mailbox_domain(db: orm.Session, domain: str) -> models.MailboxDomain:
    return db.get(models.MailboxDomain, {"domain": domain})

def create_mailbox_domain(
    db: orm.Session, domain: str, mailbox_domain: str
) -> models.MailboxDomain:
    try:
        db_dom = models.MailboxDomain(
            domain = domain,
            mailbox_domain = mailbox_domain,
        )
        db.add(db_dom)
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_dom)
    return db_dom

def delete_mailbox_domain(db: orm.Session, domain: str) -> int:
    db_dom = get_mailbox_domain(db, domain)
    if db_dom is not None:
        db.delete(db_dom)
        db.commit()
        return 1
    return 0
 

def get_alias_domain(db: orm.Session, domain: str) -> models.AliasDomain:
    return db.get(models.AliasDomain, {"domain": domain})

def create_alias_domain(
    db: orm.Session, domain: str, alias_domain: str
) -> models.AliasDomain:
    try:
        db_dom = models.AliasDomain(
            domain = domain,
            alias_domain = alias_domain,
        )
        db.add(db_dom)
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_dom)
    return db_dom

def delete_alias_domain(db: orm.Session, domain: str) -> int:
    db_dom = get_alias_domain(db, domain)
    if db_dom is not None:
        db.delete(db_dom)
        db.commit()
        return 1
    return 0

