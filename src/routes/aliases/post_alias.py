import logging

import fastapi

from ... import auth, sql_postfix, web_models
from .. import dependencies, routers


@routers.aliases.post(
    "/",
    description="Creates an alias in postfix",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=web_models.Alias,
)
async def post_alias(
    alias: web_models.CreateAlias,
    user: auth.DependsTokenUser,
    db: dependencies.DependsPostfixDb,
    domain_name: str,
) -> web_models.Alias:
    """Create an alias in postfix.

    To create an alias, you must be an admin user.

    Args:
        alias (web_models.CreateAlias): Alias information
        user (auth.DependsTokenUser): User credentials
        db (dependencies.DependsPostfixDb): Database session
        domain_name (str): Domain name

    Returns:
        web_models.Alias: Alias information

    Raises:
        fastapi.HTTPException: Alias already exists
        fastapi.HTTPException: Permission denied

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsTokenUser
        dependencies.DependsPostfixDb
        sql_postfix.create_alias
        sql_postfix.get_alias
        web_models.Alias.from_db
    """
    log = logging.getLogger(__name__)

    perms = user.get_creds()
    if not perms.can_read(domain_name):
        log.info(f"Cet utilisateur n'a pas les droits sur le domaine {domain_name}")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    name = alias.user_name + "@" + domain_name
    db_alias = sql_postfix.get_alias(db, name, alias.destination)
    if db_alias is not None:
        log.info("Cet alias existe deja")
        raise fastapi.HTTPException(status_code=409, detail="Alias already exists")

    db_alias = sql_postfix.create_alias(db, domain_name, alias.user_name, alias.destination)

    return web_models.Alias.from_db(db_alias)
