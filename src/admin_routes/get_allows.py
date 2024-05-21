from .. import auth, sql_api, web_models
from . import DependsApiDb, allows


@allows.get("/")
async def get_allows(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    username: str = "",
    domain: str = "",
) -> list[web_models.WAllowed]:
    allows = sql_api.get_api_allows(db, username, domain)
    return allows
