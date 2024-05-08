from fastapi import APIRouter

mailboxes = APIRouter(prefix="/mailboxes", tags=["mailboxes"])

from .mailbox import Mailbox, MailboxType

# from .post_user import post_user
