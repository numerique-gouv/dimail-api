import uuid
import logging


import fastapi
from ..dependencies import DependsDovecotDb

from src import auth, web_models, sql_api
from . import router


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


@router.get(
    "/",
    responses={
        200: {"description": "Get users from query request"},
        403: {"description": "Permission denied, insuficient permissions to perform the request"},
        404: {"description": "No users matched the query"},
    },
)
async def get_mailboxes(
    db: DependsDovecotDb,
    user: auth.DependsTokenUser,
    domain_name: str,
    #  page_size: int = 20,
    #  page_number: int = 0,
) -> list[web_models.Mailbox]:
    log = logging.getLogger(__name__)
    log.info(f"Searching mailboxes in domain {domain_name}\n")

    perms = user.get_creds()

    if domain_name in ["all", "example.com"]:
        if "example.com" not in perms.domains:
            return []
        return example_users

    if domain_name != "all":
        domain_db = sql_api.get_domain(db, domain_name)
        if domain_db is None:
            raise fastapi.HTTPException(status_code=404, detail="Domain not found")

        if not perms.can_read(domain_name):
            raise fastapi.HTTPException(status_code=403, detail="Permission denied")
        else:
            return []
            # return [domaine_db.mailboxes]
