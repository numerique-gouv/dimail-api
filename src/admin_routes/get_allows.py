from .. import sql_api, web_models
from . import DependsApiDb, allows


@allows.get("/")
async def get_allows(
    db: DependsApiDb,
    user: str = "",
    domain: str = "",
) -> list[web_models.WAllowed]:
    allows = sql_api.get_api_allows(db, user, domain)
    return allows
