from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.users.get("/")
async def get_users(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.User]:
    users = sql_api.get_users(db)
    return [web_models.User.from_db(user) for user in users]
