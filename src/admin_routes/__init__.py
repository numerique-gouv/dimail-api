import fastapi

users = fastapi.APIRouter(
    prefix="/admin/users",
    tags=["admin users"],
)

domains = fastapi.APIRouter(
    prefix="/admin/domains",
    tags=["admin domains"],
)

allows = fastapi.APIRouter(prefix="/admin/allows", tags=["admin allows"])

from .get_allows import get_allows
from .get_domains import get_domains
from .get_user import get_user
from .get_users import get_users
from .post_allow import post_allow
from .post_domain import post_domain
from .post_user import post_user
