import typing
import uuid

import fastapi

from .. import sql_api, web_models
from . import get_creds, mailboxes

example_users = [
    web_models.Mailbox(
        type="mailbox",
        status="broken",
        email="those users are faked in code",
        uuid=uuid.uuid4(),
    ),
    web_models.Mailbox(
        type="mailbox", status="broken", email="toto@example.com", uuid=uuid.uuid4()
    ),
    web_models.Mailbox(
        type="mailbox", status="broken", email="titi@example.com", uuid=uuid.uuid4()
    ),
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
) -> list[web_models.Mailbox]:
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
