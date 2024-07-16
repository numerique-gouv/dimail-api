import fastapi

from ... import auth, config, sql_api, web_models
from .. import routers, dependencies

@routers.domains.patch(
    "/{domain_name}",
    response_model=web_models.Domain,
    summary="Update a domain",
    description="Update a domain by name",
    status_code=fastapi.status.HTTP_200_OK,
)
async def patch_domain(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain_name: str,
    domain: web_models.DomainPatch,
) -> web_models.Domain:
    if not config.debug:
        raise fastapi.HTTPException(status_code=501, detail="Not implemented")
    domain_db = sql_api.get_domain(db, domain_name)
    if domain_db is None:
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    domain_db = sql_api.update_domain(db, domain_name, domain)
    return web_models.Domain.from_db(domain_db)
