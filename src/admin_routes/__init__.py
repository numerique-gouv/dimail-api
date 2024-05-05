from fastapi import APIRouter

users = APIRouter(
    prefix="/admin/users",
    tags=["admin users"],
)

domains = APIRouter(
    prefix="/admin/domains",
    tags=["admin domains"],
)

allows = APIRouter (
    prefix="/admin/allows",
    tags=["admin allows"]
)

from .get_users import get_users
from .get_user import get_user
from .post_user import post_user

from .get_domains import get_domains
from .post_domain import post_domain

from .get_allows import get_allows
from .post_allow import post_allow
