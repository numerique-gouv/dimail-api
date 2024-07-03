from .. import auth, web_models
from . import routers


@routers.token.get("/")
async def login_for_access_token(
    user: auth.DependsBasicUser,
) -> web_models.Token:
    token = user.create_token()
    return web_models.Token(access_token=token, token_type="bearer")
