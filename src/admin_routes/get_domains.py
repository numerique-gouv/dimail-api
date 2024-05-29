from .. import auth, sql_api, web_models
from . import DependsApiDb, domains


@domains.get("/")
async def get_domains(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.WDomain]:
    domains = sql_api.get_domains(db)
    return domains
