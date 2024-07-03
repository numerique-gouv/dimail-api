from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.allows.get("/")
async def get_allows(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    username: str = "",
    domain: str = "",
) -> list[web_models.Allowed]:
    allows = sql_api.get_allows(db, username, domain)
    return [web_models.Allowed.from_db(allow) for allow in allows]
