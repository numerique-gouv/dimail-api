"""CRUD operations for Postfix Aliases.

This module implements the CRUD operations for Postfix Aliases.

Functions:
    - get_alias (models.PostfixAlias): Get an alias by its name and destination.
    - get_aliases_by_domain (List[models.PostfixAlias]): Get all aliases for a domain.
    - get_aliases_by_name (List[models.PostfixAlias]): Get all aliases by their name.
    - create_alias (models.PostfixAlias): Create a new alias.
    - delete_alias (int): Delete an alias.
    - delete_aliases_by_name (int): Delete all aliases by their name.
"""
import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def get_alias(db: orm.Session, alias: str, destination: str):
    """Get an alias by its name and destination.

    Args:
        db (orm.Session): Database session.
        alias (str): Alias name.
        destination (str): Alias destination.

    Returns:
        models.PostfixAlias: Postfix Alias.
    """
    return db.get(models.PostfixAlias, {"alias": alias, "destination": destination})


def get_aliases_by_domain(db: orm.Session, domain: str):
    """Get all aliases for a domain.

    Args:
        db (orm.Session): Database session.
        domain (str): Domain name.

    Returns:
        List[models.PostfixAlias]: List of Postfix Aliases.
    """
    return (
        db.query(models.PostfixAlias).filter(models.PostfixAlias.domain == domain).all()
    )


def get_aliases_by_name(db: orm.Session, name: str):
    """Get all aliases by their name.

    Args:
        db (orm.Session): Database session.
        name (str): Alias name.

    Returns:
        List[models.PostfixAlias]: List of Postfix Aliases.
    """
    return db.query(models.PostfixAlias).filter(models.PostfixAlias.alias == name).all()


def create_alias(
    db: orm.Session, domain: str, username: str, destination: str
) -> models.PostfixAlias:
    """Create a new alias.

    Args:
        db (orm.Session): Database session.
        domain (str): Domain name.
        username (str): Username.
        destination (str): Destination.

    Returns:
        models.PostfixAlias: Postfix Alias.

        None: If an error occurred.
    """
    try:
        alias = username + "@" + domain
        db_alias = models.PostfixAlias(
            alias=alias,
            domain=domain,
            destination=destination,
        )
        db.add(db_alias)
        db.commit()
    except Exception:
        db.rollback()
        return None
    db.refresh(db_alias)
    return db_alias


def delete_alias(db: orm.Session, alias: str, destination: str) -> int:
    """Delete an alias.

    Args:
        db (orm.Session): Database session.
        alias (str): Alias name.
        destination (str): Alias destination.

    Returns:
        int: Number of deleted aliases

        0: If no alias was deleted.
    """
    db_alias = get_alias(db, alias, destination)
    if db_alias is not None:
        db.delete(db_alias)
        db.commit()
        return 1
    return 0


def delete_aliases_by_name(db: orm.Session, name: str):
    """Delete all aliases by their name.

    Args:
        db (orm.Session): Database session.
        name (str): Alias name.

    Returns:
        int: Number of deleted aliases

        0: If no alias was deleted.
    """
    res = db.execute(sa.delete(models.PostfixAlias).where(models.PostfixAlias.alias == name))
    db.commit()
    return res.rowcount
