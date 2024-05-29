import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def nb_users(db: orm.Session) -> int:
    return db.query(models.DBUser).count()


def get_users(db: orm.Session):
    return db.query(models.DBUser).all()


def get_user(db: orm.Session, user_name: str):
    return db.get(models.DBUser, user_name)
    return db.execute(
        sa.select(models.DBUser).where(models.DBUser.name == user_name)
    ).first()
    return db.query(models.DBUser).filter(models.DBUser.name == user_name).first()


def get_domains(db: orm.Session):
    return db.query(models.DBDomain).all()


def get_domain(db: orm.Session, domain_name: str):
    return db.get(models.DBDomain, domain_name)
    return db.query(models.DBDomain).filter(models.DBDomain.name == domain_name).first()


def create_user(db: orm.Session, name: str, password: str, is_admin: bool):
    db_user = models.DBUser(
        name=name,
        is_admin=is_admin,
    )
    db_user.set_password(password)
    try:
        db.add(db_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
    db.refresh(db_user)
    return db_user


def delete_user(db: orm.Session, user_name: str):
    db_user = db.query(models.DBUser).filter(models.DBUser.name == user_name).first()
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user


def create_domain(
    db: orm.Session,
    name: str,
    features: list[str],
    webmail_domain: str | None = None,
    mailbox_domain: str | None = None,
    imap_domains: list[str] | None = None,
    smtp_domains: list[str] | None = None,
) -> models.DBDomain:
    db_domain = models.DBDomain(
        name=name, features=[str(f) for f in features]
    )
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


def get_allows(db: orm.Session, user: str = "", domain: str = ""):
    query = db.query(models.DBAllowed)
    if user != "":
        query = query.filter_by(user=user)
    if domain != "":
        query = query.filter_by(domain=domain)
    return query.all()


def get_allowed(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    return db.get(models.DBAllowed, {"domain": domain, "user": user })
    return db.query(models.DBAllowed).filter_by(domain=domain, user=user).first()


def allow_domain_for_user(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Says the domain is allowed for the user. The user can manage mailboxes and
    aliases on that domain."""
    db_allowed = models.DBAllowed(domain=domain, user=user)
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed


def deny_domain_for_user(db: orm.Session, user: str, domain: str) -> None:
    """Says the domain is denied (not allowed anymore) for the user. The user will
    not anymore be able to manage the aliases and the mailboxes on that domain."""
    db_allowed = get_allowed(db, user, domain)
    if db_allowed is None:
        raise Exception("Domain already denied for this user")
    db.delete(db_allowed)
    db.commit()
    return None
