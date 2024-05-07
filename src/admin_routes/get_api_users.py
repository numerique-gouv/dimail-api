import fastapi

from .. import sql_api
from . import ox


@ox.get("/api/users")
async def get_api_users(
    db=fastapi.Depends(sql_api.get_api_db),
) -> list[sql_api.WApiUser]:
    users = sql_api.get_api_users(db)
    return users
