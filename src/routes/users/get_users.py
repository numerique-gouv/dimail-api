from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.users.get(
    "/",
    response_model=list[web_models.User],
    responses={
        200: {"description": "Users"},
    },
    status_code=200,
    description="Get all users",
)
async def get_users(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
) -> list[web_models.User]:
    """Get all users.

    To get all users, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        user (auth.DependsBasicAdmin): User credentials

    Returns:
        list[web_models.User]: List of users

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        routers
        sql_api.get_users
        web_models.User
    """
    users = sql_api.get_users(db)
    return [web_models.User.from_db(user) for user in users]
