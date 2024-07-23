# ruff: noqa: E402
"""This module contains the users routes.

The users routes are used to manage users.

Permitted roles:
    * admin

The users routes are:
    * DELETE /users/{user_name}
    * GET /users/{user_name}
    * GET /users
    * PATCH /users/{user_name}
    * POST /users
"""
from .delete_user import delete_user
from .get_user import get_user
from .get_users import get_users
from .patch_user import patch_user
from .post_user import post_user

__all__ = [
    delete_user,
    get_user,
    get_users,
    patch_user,
    post_user,
]

