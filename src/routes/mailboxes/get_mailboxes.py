import uuid
import logging


import fastapi
from ..dependencies import DependsDovecotDb

from src import auth, web_models, sql_dovecot, oxcli
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
):
    log = logging.getLogger(__name__)
    log.info(f"Searching mailboxes in domain {domain_name}\n")

    perms = user.get_creds()

    # FIXME To be removed
    if domain_name in ["all", "example.com"]:
        if "example.com" not in perms.domains:
            return []
        return example_users

    if not perms.can_read(domain_name):
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    # Find the expected domain
    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain_name)
    if ctx is None:
        log.error(f"Le domaine {domain_name} est inconnu du cluster OX")
        raise Exception("Le domaine est connu de la base API, mais pas de OX")

    ox_users = []
    if ctx:
        ox_users = ctx.list_users()

    db_users = sql_dovecot.get_users(db, domain_name)

    emails = set([user.email for user in ox_users] + [user.email() for user in db_users])
    ox_users_dict = {user.email: user for user in ox_users}
    db_users_dict = {user.email(): user for user in db_users}

    my_mailboxes = [
        web_models.Mailbox.from_both_users(
            ox_users_dict.get(email),
            db_users_dict.get(email),
        )
        for email in emails
    ]

    return my_mailboxes
