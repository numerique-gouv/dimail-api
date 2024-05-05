from fastapi import APIRouter

oxusers = APIRouter(
    prefix="/users",
    tags=["users"]
)

from .get_users import get_users
from .get_user import get_user
#from .post_user import post_user

