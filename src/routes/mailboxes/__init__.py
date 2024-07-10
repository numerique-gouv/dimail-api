# ruff: noqa: E402
from .delete_mailbox import delete_mailbox
from .get_mailboxes import get_mailboxes
from .get_mailbox import get_mailbox
from .patch_mailbox import patch_mailbox
from .post_mailbox import post_mailbox

__all__ = [
    delete_mailbox,
    get_mailboxes,
    get_mailbox,
    patch_mailbox,
    post_mailbox,
]
