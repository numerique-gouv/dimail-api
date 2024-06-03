# ruff: noqa: E402

import typing

import fastapi.security
import sqlalchemy.orm as orm

from .. import sql_api, sql_dovecot, sql_postfix

mailboxes = fastapi.APIRouter(prefix="/mailboxes", tags=["mailboxes"])
aliases = fastapi.APIRouter(prefix="/aliases", tags=["aliases"])
token = fastapi.APIRouter(prefix="/token", tags=["token"])


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

from .get_alias import get_alias
from .get_mailbox import get_mailbox
from .get_mailboxes import get_mailboxes
from .get_token import login_for_access_token
from .post_alias import post_alias
from .post_mailbox import post_mailbox

__all__ = [
    get_alias,
    get_mailbox,
    get_mailboxes,
    login_for_access_token,
    post_alias,
    post_mailbox,
]
