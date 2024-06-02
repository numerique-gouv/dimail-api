from .. import auth, sql_api, web_models
from . import DependsApiDb, allows


@allows.get("/")
async def get_allows(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    username: str = "",
    domain: str = "",
) -> list[web_models.Allowed]:
    allows = sql_api.get_allows(db, username, domain)
    return [web_models.Allowed.from_db(allow) for allow in allows]
