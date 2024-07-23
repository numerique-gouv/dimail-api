"""This modules contains the dependencies for the authentication of the users.

The dependencies are used to check the user's role and permissions before
executing the endpoint's function. The dependencies are used in the FastAPI

Example:
    To use the dependencies, you need to import them in the endpoint's file and
    add them to the endpoint's function as a parameter.

    ```python

    from fastapi import APIRouter, Depends
    from src.auth import DependsBasicUser
    from src.models import User

    router = APIRouter()

    @router.get("/users/me")
    async def read_users_me(user: User = Depends(DependsBasicUser)):
        return user
    ```

    In this example, the endpoint `/users/me` will return the user object if the
    user is a basic user. If the user is not a basic user, the endpoint will
    return a 403 Forbidden error.

The export class are:
    - DependsBasicAdmin: checks if the user is an admin
    - DependsBasicUser: checks if the user is a basic user
    - DependsTokenUser: checks if the user has a valid JWT token
"""
from .basic_admin import DependsBasicAdmin
from .basic_user import DependsBasicUser
from .token_user import DependsTokenUser

__all__ = [DependsBasicAdmin, DependsBasicUser, DependsTokenUser]
