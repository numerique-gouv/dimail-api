import fastapi

from .. import auth, sql_api, web_models
from . import DependsApiDb, users


@users.get("/{user_name}")
async def get_user(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    user_name: str,
) -> web_models.WUser:
    user_db = sql_api.get_api_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return user_db
