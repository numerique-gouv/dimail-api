from fastapi import APIRouter

mailboxes = APIRouter(prefix="/mailboxes", tags=["mailboxes"])

from .mailbox import Mailbox, MailboxType
from .get_mailbox import get_mailbox
from .get_mailboxes import get_mailboxes

# from .post_user import post_user
