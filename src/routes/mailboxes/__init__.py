# ruff: noqa: E402
import fastapi.security
from .. import dependencies

router = fastapi.APIRouter(prefix="/domains/{domain_name}/mailboxes", tags=["mailboxes"])

from .get_mailboxes import get_mailboxes
from .get_mailbox import get_mailbox
from .post_mailbox import post_mailbox

__all__ = [
    dependencies,
    get_mailboxes,
    get_mailbox,
    post_mailbox,
]
