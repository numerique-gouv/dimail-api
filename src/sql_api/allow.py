"""This module contains the functions to manage the allows in the database.

The allows are the permissions given to a user to manage the mailboxes and the aliases
The allows are stored in the table `allows` in the database. The table has the following
columns:
    - `user`: the user that is allowed to manage the domain
    - `domain`: the domain that the user is allowed to manage

The allows are managed by the following functions:
    - get_allows: get all the allows in the database
    - get_allowed: get an allow in the database
    - allow_domain_for_user: allow a domain for a user
    - deny_domain_for_user: deny a domain for a user
    - delete_allows_by_user: delete all the allows for a user

The allows are used to manage the mailboxes and the aliases. The allows are used to
determine if a user can manage the mailboxes and the aliases on a domain. If the user
is allowed to manage the domain, the user can manage the mailboxes and the aliases on
that domain. If the user is not allowed to manage the domain, the user cannot manage the
mailboxes and the aliases on that domain.
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def get_allows(db: orm.Session, user: str = "", domain: str = ""):
    """Get all the allows in the database. If the user is not empty, get the allows for
    that user. If the domain is not empty, get the allows for that domain. If both are
    not empty, get the allows for that user and that domain.

    Args:
        db (orm.Session): the database session
        user (str): the user to get the allows for
        domain (str): the domain to get the allows for

    Returns:
        List[models.DBAllowed]: the allows in the database
    """
    query = db.query(models.DBAllowed)
    if user != "":
        query = query.filter_by(user=user)
    if domain != "":
        query = query.filter_by(domain=domain)
    return query.all()


def get_allowed(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Get the allow for the user and the domain.

    Args:
        db (orm.Session): the database session
        user (str): the user to get the allow for
        domain (str): the domain to get the allow for

    Returns:
        models.DBAllowed: the allow for the user and the
    """
    return db.get(models.DBAllowed, {"domain": domain, "user": user})
    # FIXME à discuter avec Benjamin il me semble que cette ligne est morte
    return db.query(models.DBAllowed).filter_by(domain=domain, user=user).first()


def allow_domain_for_user(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Says the domain is allowed for the user. The user can manage mailboxes and
    aliases on that domain.

    Args:
        db (orm.Session): the database session
        user (str): the user that is allowed to manage the domain
        domain (str): the domain that the user is allowed to manage

    Returns:
        models.DBAllowed: the allow created in the database
    """
    db_allowed = models.DBAllowed(domain=domain, user=user)
    db.add(db_allowed)
    db.commit()
    db.refresh(db_allowed)
    return db_allowed


def deny_domain_for_user(db: orm.Session, user: str, domain: str) -> models.DBAllowed:
    """Says the domain is denied (not allowed anymore) for the user. The user will
    not anymore be able to manage the aliases and the mailboxes on that domain.

    Args:
        db (orm.Session): the database session
        user (str): the user that is not allowed to manage the domain anymore
        domain (str): the domain that the user is not allowed to manage anymore

    Returns:
        models.DBAllowed: the allow deleted in the database
    """
    db_allowed = get_allowed(db, user, domain)
    if db_allowed is not None:
        db.delete(db_allowed)
        db.commit()
    return db_allowed


def delete_allows_by_user(db: orm.Session, user: str) -> int:
    """Delete all the allows for this user.

    Args:
        db (orm.Session): the database session
        user (str): the user to delete the allows for

    Returns:
        int: the number of allows deleted
    """
    res = db.execute(sa.delete(models.DBAllowed).where(models.DBAllowed.user == user))
    db.commit()
    return res.rowcount
