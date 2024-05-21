from .. import auth, web_models
from . import token


@token.get("/")
async def login_for_access_token(
    user: auth.DependsBasicUser,
) -> web_models.WToken:
    token = user.create_token()
    return web_models.WToken(access_token=token, token_type="bearer")
