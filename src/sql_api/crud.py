import sqlalchemy as sa
import sqlalchemy.orm as orm

from .. import web_models
from . import models


def nb_users(db: orm.Session) -> int:
    return db.query(models.DBUser).count()


def get_api_users(db: orm.Session):
    return db.query(models.DBUser).all()


def get_api_user(db: orm.Session, user_name: str):
    return db.get(models.DBUser, user_name)
    return db.execute(
        sa.select(models.DBUser).where(models.DBUser.name == user_name)
    ).first()
    return db.query(models.DBUser).filter(models.DBUser.name == user_name).first()


def get_api_domains(db: orm.Session):
    return db.query(models.DBDomain).all()


def get_api_domain(db: orm.Session, domain_name: str):
    return db.get(models.DBDomain, domain_name)
    return db.query(models.DBDomain).filter(models.DBDomain.name == domain_name).first()


def create_api_user(db: orm.Session, name: str, password: str, is_admin: bool):
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


def delete_api_user(db: orm.Session, user_name: str):
    db_user = db.query(models.DBUser).filter(models.DBUser.name == user_name).first()
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user


def create_api_domain(db: orm.Session, domain: web_models.WDomain):
    db_domain = models.DBDomain(**domain.model_dump())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain


def get_api_allows(db: orm.Session, user: str, domain: str):
    query = db.query(models.DBAllowed)
    if user != "":
        query = query.filter_by(user=user)
    if domain != "":
        query = query.filter_by(domain=domain)
    return query.all()


def get_api_allowed(db: orm.Session, user: str, domain: str):
    return db.query(models.DBAllowed).filter_by(domain=domain, user=user).first()


def allow_domain_for_user(db: orm.Session, allowed: web_models.WAllowed):
    db_allowed = models.DBAllowed(**allowed.model_dump())
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed
