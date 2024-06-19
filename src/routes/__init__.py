# ruff: noqa: E402
import fastapi.security
from . import mailboxes, aliases

domains = fastapi.APIRouter(
    prefix="/domains",
    tags=["domains"],
)
token = fastapi.APIRouter(prefix="/token", tags=["token"])

from .get_domain import get_domain
from .get_token import login_for_access_token

__all__ = [
    aliases,
    get_domain,
    login_for_access_token,
    mailboxes,
]
