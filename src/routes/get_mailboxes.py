import uuid

import fastapi
import typing

from .. import sql_api
from . import get_creds, mailboxes
from .mailbox import Mailbox

example_users = [
    Mailbox(type="mailbox", email="those users are faked in code", uuid=uuid.uuid4()),
    Mailbox(type="mailbox", email="toto@example.com", uuid=uuid.uuid4()),
    Mailbox(type="mailbox", email="titi@example.com", uuid=uuid.uuid4()),
]


@mailboxes.get(
    "/",
    responses={
        200: {"description": "Get users from query request"},
        403: {
            "description": "Permission denied, insuficient permissions to perform the request"
        },
        404: {"description": "No users matched the query"},
    },
)
async def get_mailboxes(
    perms: typing.Annotated[sql_api.Creds, fastapi.Depends(get_creds)],
    domain: str = "all",
    #  page_size: int = 20,
    #  page_number: int = 0,
) -> list[Mailbox]:
    print(f"Searching users in domain {domain}\n")
    if domain == "all":
        if "example.com" not in perms.domains:
            return []
        return example_users
    if domain != "all":
        if not perms.can_read(domain):
            raise fastapi.HTTPException(status_code=403, detail="Permission denied")
        if domain != "example.com":
            return []
        return example_users
