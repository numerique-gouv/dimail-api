import sqlalchemy.orm as orm

from . import models


def get_user(db: orm.Session, username: str, domain: str):
    """Get a user by name.

    Args:
        db: the database session
        username: the name of the user
        domain: the domain of the user

    Returns:
        ImapUser: the user with the given name
    """
    return db.get(models.ImapUser, {"username": username, "domain": domain})


def get_users(db: orm.Session, domain_name: str):
    """Get all users.

    Args:
        db: the database session
        domain_name: the name of the domain

    Returns:
        list[ImapUser]: a list of all users
    """
    return db.query(models.ImapUser).filter(models.ImapUser.domain == domain_name).all()


def create_user(db: orm.Session, username: str, domain: str, password: str):
    """Create a user.

    Args:
        db: the database session
        username: the name of the user
        domain: the domain of the user
        password: the password of the user

    Returns:
        ImapUser: the created user

        None: if the user could not be created
    """
    imap_user = models.ImapUser(
        username=username,
        domain=domain,
        active="Y",
        password="WILL BE ENCODED",
        uid=0,
        gid=0,
        home="",
    )
    try:
        imap_user.set_password(password)
        db.add(imap_user)
        db.commit()
    except Exception as e:
        print(str(e))
        db.rollback()
        return None
    db.refresh(imap_user)
    return imap_user


def delete_user(db: orm.Session, username: str, domain: str):
    """Delete a user.

    Args:
        db: the database session
        username: the name of the user
        domain: the domain of the user

    Returns:
        ImapUser: the deleted user

        None: if the user could not be deleted
    """
    user = get_user(db, username, domain)
    if user is not None:
        db.delete(user)
        db.commit()
    return user
