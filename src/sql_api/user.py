import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def count_users(db: orm.Session) -> int:
    return db.query(models.DBUser).count()


def get_users(db: orm.Session):
    return db.query(models.DBUser).all()


def get_user(db: orm.Session, user_name: str):
    return db.get(models.DBUser, user_name)
    return db.execute(
        sa.select(models.DBUser).where(models.DBUser.name == user_name)
    ).first()
    return db.query(models.DBUser).filter(models.DBUser.name == user_name).first()


def create_user(db: orm.Session, name: str, password: str, is_admin: bool):
    db_user = models.DBUser(
        name=name,
        is_admin=is_admin,
    )
    try:
        db_user.set_password(password)
        db.add(db_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
        return None
    db.refresh(db_user)
    return db_user


def update_user_password(db: orm.Session, name: str, password: str):
    db_user = get_user(db, name)
    if db_user is None:
        return None
    try:
        db_user.set_password(password)
        db.flush()
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
    db.refresh(db_user)
    return db_user


def update_user_is_admin(db: orm.Session, name: str, is_admin: bool):
    db_user = get_user(db, name)
    if db_user is None:
        return None
    db_user.is_admin = is_admin
    try:
        db.flush()
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
    db.refresh(db_user)
    return db_user


def delete_user(db: orm.Session, name: str):
    db_user = get_user(db, name)
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user
