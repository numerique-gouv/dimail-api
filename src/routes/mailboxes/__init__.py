# ruff: noqa: E402
"""This module contains the mailboxes routes.

The mailboxes routes are used to manage mailboxes.

The mailboxes routes are:
    * DELETE /domains/{domain_name}/mailboxes/{user_name}
    * GET /domains/{domain_name}/mailboxes/{user_name}
    * PATCH /domains/{domain_name}/mailboxes/{user_name}
    * POST /domains/{domain_name}/mailboxes/{user_name}
"""
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
