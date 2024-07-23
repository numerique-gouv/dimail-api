import fastapi

from ... import auth, sql_api, web_models
from .. import dependencies, routers


@routers.users.post(
    "/",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=web_models.User,
    responses={
        201: {"description": "Created"},
        409: {"description": "User already exists"},
    },
    description="Create a user",
)
async def post_user(
    db: dependencies.DependsApiDb,
    admin: auth.DependsBasicAdmin,
    user: web_models.CreateUser,
) -> web_models.User:
    """Create user.

    To create a user, you must be an admin user.

    Args:
        db (dependencies.DependsApiDb): Database session
        admin (auth.DependsBasicAdmin): Admin user credentials
        user (web_models.CreateUser): User data

    Returns:
        web_models.User: Created user

    Raises:
        fastapi.HTTPException: User already exists

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsBasicAdmin
        dependencies.DependsApiDb
        routers
        sql_api.create_user
        sql_api.get_user
        web_models.CreateUser
        web_models.User
    """
    user_db = sql_api.get_user(db, user.name)

    if user_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="User already exists")

    user_db = sql_api.create_user(
        db, name=user.name, password=user.password, is_admin=user.is_admin
    )

    return web_models.User.from_db(user_db)
