# ruff: noqa: E402
from .get_mailboxes import get_mailboxes
from .get_mailbox import get_mailbox
from .patch_mailbox import patch_mailbox
from .post_mailbox import post_mailbox

__all__ = [
    get_mailboxes,
    get_mailbox,
    patch_mailbox,
    post_mailbox,
]
