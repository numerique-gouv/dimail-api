import typing

from .. import sql_dovecot, sql_postfix, sql_api

import fastapi.security
import sqlalchemy.orm as orm


def depends_api_db():
    """Dependency for fastapi that creates an orm session and yields it. Ensures
    the session is closed at the end."""
    maker = sql_api.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()


DependsApiDb = typing.Annotated[orm.Session, fastapi.Depends(depends_api_db)]


def depends_dovecot_db():
    """Dependency for fastapi that creates an orm session and yields it. Ensures
    the session is closed at the end."""
    maker = sql_dovecot.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()


DependsDovecotDb = typing.Annotated[typing.Any, fastapi.Depends(depends_dovecot_db)]


def depends_postfix_db():
    """Dependency for fastapi that creates an orm session and yields it. Ensures
    the session is closed at the end."""
    maker = sql_postfix.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()


DependsPostfixDb = typing.Annotated[typing.Any, fastapi.Depends(depends_postfix_db)]
