from .. import auth, sql_api, web_models
from . import DependsApiDb, domains


@domains.get("/")
async def get_domains(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.Domain]:
    domains = sql_api.get_domains(db)
    return [web_models.Domain.from_db(dom) for dom in domains]
