import typing

import fastapi
import sqlalchemy.orm as orm

from .. import sql_api

users = fastapi.APIRouter(
    prefix="/admin/users",
    tags=["admin users"],
)

domains = fastapi.APIRouter(
    prefix="/admin/domains",
    tags=["admin domains"],
)

allows = fastapi.APIRouter(prefix="/admin/allows", tags=["admin allows"])


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

from .delete_allow import delete_allow
from .get_allows import get_allows
from .get_domains import get_domains
from .get_user import get_user
from .get_users import get_users
from .post_allow import post_allow
from .post_domain import post_domain
from .post_user import post_user

__all__ = [
    delete_allow,
    get_allows,
    get_domains,
    get_user,
    get_users,
    post_allow,
    post_domain,
    post_user,
]
