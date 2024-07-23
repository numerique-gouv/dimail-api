"""SQL API for user management.

This module contains the functions to interact with the SQL database for user management.

Functions:
    - count_users: count the number of users in the database
    - get_users: get all users
    - get_user: get a user by name
    - create_user: create a user
    - update_user_password: update a user's password
    - update_user_is_admin: update a user's admin status
    - delete_user: delete a user
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def count_users(db: orm.Session) -> int:
    """Count the number of users in the database.

    Args:
        db: the database session

    Returns:
        int: the number of users in the database
    """
    return db.query(models.DBUser).count()


def get_users(
        db: orm.Session
)-> list[models.DBUser] | None:
    """Get all users.

    Args:
        db: the database session

    Returns:
        list[DBUser]: a list of all users
    """
    return db.query(models.DBUser).all()


def get_user(
        db: orm.Session,
        user_name: str
)-> models.DBUser | None:
    """Get a user by name.

    Args:
        db: the database session
        user_name: the name of the user

    Returns:
        DBUser: the user with the given name
    """
    return db.get(models.DBUser, user_name)
    # FIXME: deadline?
    return db.execute(
        sa.select(models.DBUser).where(models.DBUser.name == user_name)
    ).first()
    return db.query(models.DBUser).filter(models.DBUser.name == user_name).first()


def create_user(
        db: orm.Session,
        name: str,
        password: str,
        is_admin: bool
)-> models.DBUser | None:
    """Create a user.

    Args:
        db: the database session
        name: the name of the user
        password: the password of the user
        is_admin: whether the user is an admin

    Returns:
        DBUser: the created user
        None: if the user could not be created
    """
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


def update_user_password(
        db: orm.Session,
        name: str,
        password: str
)-> models.DBUser | None:
    """Update a user's password.

    Args:
        db: the database session
        name: the name of the user
        password: the new password

    Returns:
        DBUser: the updated user
        None: if the user could not be updated
    """
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


def update_user_is_admin(
        db: orm.Session,
        name: str, is_admin: bool
) -> models.DBUser | None:
    """Update a user's admin status.

    Args:
        db: the database session
        name: the name of the user
        is_admin: whether the user is an admin

    Returns:
        DBUser: the updated user
        None: if the user could not be updated
    """
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


def delete_user(db: orm.Session, name: str) -> models.DBUser | None:
    """Delete a user.

    Args:
        db: the database session
        name: the name of the user

    Returns:
        DBUser: the deleted user

        None: if the user could not be deleted
    """
    db_user = get_user(db, name)
    if db_user is not None:
        db.delete(db_user)
        db.commit()
    return db_user
