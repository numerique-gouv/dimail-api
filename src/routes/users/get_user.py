import fastapi

from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.users.get(
    "/{user_name}",
    response_model=web_models.User,
    responses={
        200: {"description": "User"},
        404: {"description": "User not found"},
    },
    status_code=fastapi.status.HTTP_200_OK,
)
async def get_user(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    user_name: str,
) -> web_models.User:
    user_db = sql_api.get_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return web_models.User.from_db(user_db)
