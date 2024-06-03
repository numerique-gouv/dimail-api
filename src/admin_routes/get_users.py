from .. import auth, sql_api, web_models
from . import DependsApiDb, users


@users.get("/")
async def get_users(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.User]:
    users = sql_api.get_users(db)
    return [web_models.User.from_db(user) for user in users]
