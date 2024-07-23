"""Dependencies for fastapi routes. These dependencies are used to create
orm sessions for the routes. The sessions are closed at the end of the route.

Example:

    To use the dependencies, you need to import them in the endpoint's file and add
    them to the endpoint's function as a parameter.

    ```python

    from fastapi import APIRouter, Depends
    from src.routes import DependsApiDb
    from src.models import User

    router = APIRouter()

    @router.get("/users/me")
    async def read_users_me(user: User = Depends(DependsApiDb)):
        return user
    ```

    In this example, the endpoint `/users/me` will return the user object if the
    user is a basic user. If the user is not a basic user,
    the endpoint will return a 403 Forbidden error.

The export class are:
    - DependsApiDb: checks if the user is an admin
    - DependsDovecotDb: checks if the user is a basic user
    - DependsPostfixDb: checks if the user has a valid JWT token

Dependencies:
    - fastapi
    - sqlalchemy.orm
    - sql_dovecot
    - sql_postfix
    - sql_api

See also:
    - https://fastapi.tiangolo.com/tutorial/dependencies
    - https://fastapi.tiangolo.com/tutorial/sql-databases
    - https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
    - https://fastapi.tiangolo.com/tutorial/security/simple-verify-token
"""
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
