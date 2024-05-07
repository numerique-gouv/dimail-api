from fastapi import APIRouter

oxusers = APIRouter(prefix="/users", tags=["users"])

from .get_user import get_user
from .get_users import get_users

# from .post_user import post_user
