import fastapi

from .. import sql_api, web_models
from . import DependsApiDb, domains


@domains.post("/")
async def post_domain(
    db: DependsApiDb,
    domain: web_models.WDomain,
) -> web_models.WDomain:
    domain_db = sql_api.get_api_domain(db, domain.name)

    if domain_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="Domain already exists")

    return sql_api.create_api_domain(db, domain)
