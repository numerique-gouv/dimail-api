import uuid

from fastapi import Depends

from src.creds import Creds, get_creds

from . import oxusers
from .user import User

example_users = [
    User(email="those users are faked in code", uuid=uuid.uuid4()),
    User(email="toto@example.com", uuid=uuid.uuid4()),
    User(email="titi@example.com", uuid=uuid.uuid4()),
]


@oxusers.get(
    "/",
    responses={
        200: {"description": "Get users from query request"},
        403: {
            "description": "Permission denied, insuficient permissions to perform the request"
        },
        404: {"description": "No users matched the query"},
    },
)
async def get_users(
    creds: Creds = Depends(get_creds),
    domain: str = "all",
    #  page_size: int = 20,
    #  page_number: int = 0,
) -> list[User]:
    print(f"Searching users in domain {domain}\n")
    if domain == "all":
        if "example.com" not in creds.domains:
            return []
        return example_users
    if domain != "all":
        if domain not in creds.domain:
            raise HTTPException(status_code=403, detail="Permission denied")
        if domain != "example.com":
            return []
        return example_users
