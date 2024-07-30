import datetime

import sqlalchemy.orm as orm

from . import models


def get_domains(db: orm.Session):
    return db.query(models.DBDomain).all()


def get_domain(db: orm.Session, domain_name: str):
    return db.get(models.DBDomain, domain_name)
    return db.query(models.DBDomain).filter(models.DBDomain.name == domain_name).first()


def create_domain(
    db: orm.Session,
    name: str,
    features: list[str],
    webmail_domain: str | None = None,
    mailbox_domain: str | None = None,
    imap_domains: list[str] | None = None,
    smtp_domains: list[str] | None = None,
    dkim_selector: str | None = None,
    dkim_private: str | None = None,
    dkim_public: str | None = None,
) -> models.DBDomain:
    db_domain = models.DBDomain(name=name, features=[str(f) for f in features])
    if webmail_domain is not None:
        db_domain.webmail_domain = webmail_domain
    if mailbox_domain is not None:
        db_domain.mailbox_domain = mailbox_domain
    if imap_domains is not None:
        db_domain.imap_domains = [dom for dom in imap_domains]
    if smtp_domains is not None:
        db_domain.smtp_domains = [dom for dom in smtp_domains]
    if dkim_selector is not None:
        db_domain.dkim_selector = dkim_selector
    if dkim_private is not None:
        db_domain.dkim_private = dkim_private
    if dkim_public is not None:
        db_domain.dkim_public = dkim_public
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain


def update_domain_state(db: orm.Session, name: str, state: str) -> models.DBDomain:
    db_domain = get_domain(db, name)
    if db_domain is None:
        return None
    try:
        db_domain.state = state
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_domain)
    return db_domain


def update_domain_errors(
    db: orm.Session, name: str, errors: list[str] | None
) -> models.DBDomain:
    db_domain = get_domain(db, name)
    if db_domain is None:
        return None
    try:
        db_domain.errors = errors
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_domain)
    return db_domain


def update_domain_dtchecked(
    db: orm.Session, name: str, dtchecked: datetime.datetime | str | None = None
) -> models.DBDomain:
    if dtchecked is None:
        dtchecked = datetime.datetime.now(datetime.timezone.utc)
    if isinstance(dtchecked, str):
        if dtchecked == "now":
            dtchecked = datetime.datetime.now(datetime.timezone.utc)
        else:
            raise Exception("La seule chaine possible ici est 'now'")
    if not isinstance(dtchecked, datetime.datetime):
        raise Exception(f"Je ne peux pas mettre '{dtchecked}' comme date de dernier controle du domaine")
    db_domain = get_domain(db, name)
    if db_domain is None:
        return None
    try:
        db_domain.dtchecked = dtchecked
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_domain)
    return db_domain


def update_domain_dtaction(
    db: orm.Session, name: str, dtaction: datetime.datetime
) -> models.DBDomain:
    db_domain = get_domain(db, name)
    if db_domain is None:
        return None
    try:
        db_domain.dtaction = dtaction
        db.flush()
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_domain)
    return db_domain


def first_domain_need_action(db: orm.Session) -> models.DBDomain:
    db_domain = ( db.query(models.DBDomain).
        filter(models.DBDomain.dtaction != None).
        order_by(models.DBDomain.dtaction.asc()).
        with_for_update(skip_locked=True).
        first()
    )
    return db_domain
