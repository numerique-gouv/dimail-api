import sqlalchemy as sa
import sqlalchemy.orm as orm

from . import models


def get_alias(db: orm.Session, alias: str, destination: str):
    return db.get(models.PostfixAlias, {"alias": alias, "destination": destination})


def get_aliases_by_domain(db: orm.Session, domain: str):
    return (
        db.query(models.PostfixAlias).filter(models.PostfixAlias.domain == domain).all()
    )


def get_aliases_by_name(db: orm.Session, name: str):
    return db.query(models.PostfixAlias).filter(models.PostfixAlias.alias == name).all()


def create_alias(
    db: orm.Session, domain: str, username: str, destination: str
) -> models.PostfixAlias:
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
    db_alias = get_alias(db, alias, destination)
    if db_alias is not None:
        db.delete(db_alias)
        db.commit()
        return 1
    return 0


def delete_aliases_by_name(db: orm.Session, name: str):
    res = db.execute(sa.delete(models.PostfixAlias).where(models.PostfixAlias.alias == name))
    db.commit()
    return res.rowcount
