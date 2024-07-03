# ruff: noqa: E402
import fastapi.security

from .get_alias import get_alias
from .post_alias import post_alias

__all__ = [
    get_alias,
    post_alias,
]
