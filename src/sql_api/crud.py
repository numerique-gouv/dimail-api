from sqlalchemy.orm import Session
from sqlalchemy import select

from . import models, schemas

def get_api_users(db: Session):
    return db.query(models.ApiUser).all()

def get_api_user(db: Session, user_name: str):
    return db.get(models.ApiUser, user_name)
    return db.execute(select(models.ApiUser).where(models.ApiUser.name == user_name)).first()
    return db.query(models.ApiUser).filter(models.ApiUser.name == user_name).first()

def get_api_domain(db: Session, domain_name: str):
    return db.query(models.ApiDomain).filter(models.ApiDomain.name == domain_name).first()

def create_api_user(db: Session, user: schemas.ApiUser):
    db_user = models.ApiUser(**user.model_dump())
    try:
        db.add(db_user)
        db.commit()
    except:
        db.rollback()
    db.refresh(db_user)
    return db_user

def delete_api_user(db: Session, user_name: str):
    db_user = db.query(models.ApiUser).filter(models.ApiUser.name == user_name).first()
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user

def create_api_domain(db: Session, domain: schemas.ApiDomain):
    db_domain = models.ApiDomain(**domain.model_dump())
    db.add(db_domain)
    db.commit()
    db.refresh(db_domain)
    return db_domain

def get_api_allowed(db: Session, user: str, domain: str):
    return db.query(models.ApiAllowed).filter_by(domain = domain, user = user).first()

def allow_domain_for_user(db: Session, allowed: schemas.ApiAllowed):
    db_allowed = models.ApiAllowed(**allowed.model_dump())
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed


