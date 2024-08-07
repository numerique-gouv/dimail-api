from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.domains.get("/")
async def get_domains(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.Domain]:
    domains = sql_api.get_domains(db)
    return [web_models.Domain.from_db(domain) for domain in domains]
