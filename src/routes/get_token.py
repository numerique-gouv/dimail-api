"""Get token route.

This module contains the route to get a token for the user.

Example:
    To use the route, you need to import the route in the main file and add it to the FastAPI app.

    ```python

    from fastapi import FastAPI
    from src.routes import get_token

    app = FastAPI()

    app.include_router(get_token.router)
    ```

    In this example, the route `/token` will return a token if the user is a basic user.

The export function is:
    - login_for_access_token: route to get a token for the user
"""
from .. import auth, web_models
from . import routers


@routers.token.get("/")
async def login_for_access_token(
    user: auth.DependsBasicUser,
) -> web_models.Token:
    """Route to get a token for the user.

    Args:
        user (User): the user to get the token for

    Returns:
        Token: the token for the user

    Raises:
        HTTPException: if the user is not a basic user
    """
    token = user.create_token()
    return web_models.Token(access_token=token, token_type="bearer")
