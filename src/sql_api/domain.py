"""SQL API for domain operations.

This module contains functions to interact with the database for domain operations.

Functions:
    - get_domains: Get all domains from the database.
    - get_domain: Get a domain from the database.
    - create_domain: Create a domain in the database.

Classes:
    - None

Exceptions:
    - None
"""
import sqlalchemy.orm as orm

from . import models


def get_domains(db: orm.Session):
    """Get all domains from the database.

    Args:
        db: SQLAlchemy session object.

    Returns:
        List of all domains in the database.
    """
    return db.query(models.DBDomain).all()


def get_domain(db: orm.Session, domain_name: str):
    """Get a domain from the database.

    Args:
        db: SQLAlchemy session object.

    Returns:
        Domain object from the database.
    """
    return db.get(models.DBDomain, domain_name)
    # FIXME Parler de cette ligne à benjamin il me semble qu'elle est morte
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
    """Create a domain in the database.

    Args:
        db: SQLAlchemy session object.
        name: Domain name.
        features: List of features for the domain.
        webmail_domain: Webmail domain.
        mailbox_domain: Mailbox domain.
        imap_domains: List of IMAP domains.
        smtp_domains: List of SMTP domains.

    Returns:
        Domain object from the database

    Raises:
        None
    """
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
