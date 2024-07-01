# ruff: noqa: E402
import fastapi.security
from .. import dependencies

router = fastapi.APIRouter(prefix="/domains/{domain_name}/aliases", tags=["aliases"])

from .get_alias import get_alias
from .post_alias import post_alias

__all__ = [
    dependencies,
    get_alias,
    post_alias,
]
