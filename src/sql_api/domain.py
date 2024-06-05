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

    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain
