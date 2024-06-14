# ruff: noqa: E402
import fastapi.security
from . import mailboxes

domains = fastapi.APIRouter(
    prefix="/domains",
    tags=["domains"],
)
aliases = fastapi.APIRouter(prefix="/aliases", tags=["aliases"])
token = fastapi.APIRouter(prefix="/token", tags=["token"])

from .get_alias import get_alias
from .get_domain import get_domain
from .get_token import login_for_access_token
from .post_alias import post_alias

__all__ = [
    get_alias,
    get_domain,
    get_mailbox,
    get_mailboxes,
    login_for_access_token,
    mailboxes,
    post_alias,
    post_mailbox,
]
