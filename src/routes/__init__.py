from fastapi import APIRouter

from .. import sql_api

mailboxes = APIRouter(prefix="/mailboxes", tags=["mailboxes"])


async def get_creds():
    api_db = next(sql_api.get_api_db())
    yield sql_api.get_creds(api_db)


from .get_mailbox import get_mailbox
from .get_mailboxes import get_mailboxes

# from .post_user import post_user
