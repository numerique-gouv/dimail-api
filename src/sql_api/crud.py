from passlib.hash import argon2
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import web_models
from . import models


def get_api_users(db: Session):
    return db.query(models.DBUser).all()


def get_api_user(db: Session, user_name: str):
    return db.get(models.DBUser, user_name)
    return db.execute(
        select(models.DBUser).where(models.DBUser.name == user_name)
    ).first()
    return db.query(models.DBUser).filter(models.DBUser.name == user_name).first()


def get_api_domains(db: Session):
    return db.query(models.DBDomain).all()


def get_api_domain(db: Session, domain_name: str):
    return db.get(models.DBDomain, domain_name)
    return db.query(models.DBDomain).filter(models.DBDomain.name == domain_name).first()


def verify_password(plain_password, hashed_password):
    return argon2.verify(plain_password, hashed_password)


def make_password_hash(password):
    return argon2.hash(password)


def create_api_user(db: Session, user: web_models.WUser):
    db_user = models.DBUser(**user.model_dump(exclude="password"))
    db_user.hashed_password = make_password_hash(user.password)
    try:
        db.add(db_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
    db.refresh(db_user)
    return db_user


def delete_api_user(db: Session, user_name: str):
    db_user = db.query(models.DBUser).filter(models.DBUser.name == user_name).first()
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user


def create_api_domain(db: Session, domain: web_models.WDomain):
    db_domain = models.DBDomain(**domain.model_dump())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain


def get_api_allows(db: Session, user: str, domain: str):
    query = db.query(models.DBAllowed)
    if user != "":
        query = query.filter_by(user=user)
    if domain != "":
        query = query.filter_by(domain=domain)
    return query.all()


def get_api_allowed(db: Session, user: str, domain: str):
    return db.query(models.DBAllowed).filter_by(domain=domain, user=user).first()


def allow_domain_for_user(db: Session, allowed: web_models.WAllowed):
    db_allowed = models.DBAllowed(**allowed.model_dump())
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed
