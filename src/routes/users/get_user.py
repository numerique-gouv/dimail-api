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
    description="Get a user by name",
)
async def get_user(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    user_name: str,
) -> web_models.User:
    """Get a user by name.

    To get a user, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials
        user_name (str): User name

    Returns:
        web_models.User: User

    Raises:
        fastapi.HTTPException: User not found

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        routers
        sql_api.get_user
        web_models.User
    """
    user_db = sql_api.get_user(db, user_name)
    if user_db is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return web_models.User.from_db(user_db)
