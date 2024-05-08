import fastapi

from .. import sql_api, web_models
from . import ox


@ox.get("/api/users")
async def get_api_users(
    db=fastapi.Depends(sql_api.get_api_db),
) -> list[web_models.WUser]:
    users = sql_api.get_api_users(db)
    return users
