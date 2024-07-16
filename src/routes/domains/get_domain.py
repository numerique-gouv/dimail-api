import logging

import fastapi

from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.domains.get(
    "/{domain_name}",
    response_model=web_models.Domain,
    summary="Get a domain",
    description="Get a domain by name",
)
async def get_domain(
    db: dependencies.DependsApiDb,
    user: auth.DependsTokenUser,
    domain_name: str,
) -> web_models.Domain:
    """Get a domain by name.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsTokenUser): User credentials
        domain_name (str): Domain name

    Returns:
        web_models.Domain: Domain information

    Raises:
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: Not authorized

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        dependencies.DependsApiDb
        routers
        sql_api.get_domain
        web_models
    """
    log = logging.getLogger(__name__)
    perms = user.get_creds()

    domain_db = sql_api.get_domain(db, domain_name)
    if domain_db is None:
        log.info(f"Domain {domain_name} not found.")
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for user.")
        raise fastapi.HTTPException(status_code=401, detail="Not authorized.")

    return web_models.Domain.from_db(domain_db)
