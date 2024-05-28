import sqlalchemy.orm as orm

from . import models


def get_alias(db: orm.Session, alias: str, destination: str):
    return db.get(models.PostfixAlias, {"alias": alias, "destination": destination})


def get_aliases(db: orm.Session, domain: str):
    return db.query(models.PostfixAlias).filter(models.PostfixAlias.domain == domain).all()


def create_alias(
    db: orm.Session,
    domain: str,
    username: str,
    destination: str
) -> models.PostfixAlias:
    alias = username + "@" + domain
    db_alias = models.PostfixAlias(
        alias=alias,
        domain=domain,
        destination=destination,
    )
    try:
        db.add(db_alias)
        db.commit()
    except Exception as e:
        db.rollback()
        return None
    db.refresh(db_alias)
    return db_alias


