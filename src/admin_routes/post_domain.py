import fastapi

from .. import auth, oxcli, sql_api, web_models
from . import DependsApiDb, domains


@domains.post("/")
async def post_domain(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain: web_models.WDomain,
) -> web_models.WDomain:
    domain_db = sql_api.get_api_domain(db, domain.name)

    if domain_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="Domain already exists")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_name(domain.context_name)
    if ctx is None:
        ctx = ox_cluster.create_context(None, domain.context_name, domain.name)
    else:
        ctx.add_mapping(domain.name)

    return sql_api.create_api_domain(db, domain)
