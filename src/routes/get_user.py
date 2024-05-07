import re
import uuid

from fastapi import Depends, HTTPException

from src.creds import Creds, get_creds

from . import oxusers
from .user import User

mail_re = re.compile("^(?P<username>[^@]+)@(?P<domain>[^@]+)$")
uuid_re = re.compile("^[0-9a-f-]{32,36}$")


@oxusers.get(
    "/{user_id}",
    responses={
        200: {"description": "Get a user from his e_mail"},
        403: {"description": "Permission denied"},
        404: {"description": "User not found"},
    },
    description="The expected user_id can be the e-mail address of the uuid of a user",
)
async def get_user(
    user_id: str,
    creds: Creds = Depends(get_creds),
) -> User:
    test_uuid = uuid_re.match(user_id)
    test_mail = mail_re.match(user_id)
    user = User(
        email="toto@example.com",
        givenName="Given",
        surName="Sur",
        displayName="Given Sur",
        username="toto",
        domain="example.com",
        uuid=uuid.UUID("d437abd5-2b49-47db-be49-05f79f1cc242"),
    )
    domain = None
    if test_uuid is not None:
        # We try to parse the uuid (which is good enough to match the regexp)
        # if it valid, and is the uuid of an existing user, we go on for this user
        id = None
        try:
            id = uuid.UUID(user_id)
        except:
            pass

        # we have only one user here :)
        if id == user.uuid:
            domain = user.domain
        else:
            raise HTTPException(status_code=404, detail="User not found")

    if test_mail is not None:
        infos = test_mail.groupdict()
        domain = infos["domain"]

    if domain is None:
        raise HTTPException(status_code=422, detail="Invalid email address")

    if not creds.can_read(domain):
        print(f"Permission denied on domain")
        raise HTTPException(status_code=403, detail="Permission denied")

    if (
        user_id != "toto@example.com"
        and user_id != "d437abd5-2b49-47db-be49-05f79f1cc242"
    ):
        raise HTTPException(status_code=404, detail="User not found")

    return user
