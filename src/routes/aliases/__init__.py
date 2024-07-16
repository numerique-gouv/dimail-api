# ruff: noqa: E402
"""This module contains the allows routes.

The allows routes are used to manage allows.

Permitted roles:
    * admin
    * user if is admin of the domain

The allows routes are:
    * GET /aliases/{alias}
    * POST /aliases
    * DELETE /aliases/{alias}
"""
from .get_alias import get_alias
from .post_alias import post_alias
from .delete_alias import delete_alias

__all__ = [
    delete_alias,
    get_alias,
    post_alias,
]
