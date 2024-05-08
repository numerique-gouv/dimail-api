from typing import Optional

import fastapi

from .. import sql_api
from . import allows


@allows.get("/")
async def get_allows(
    user: str = "",
    domain: str = "",
    db=fastapi.Depends(sql_api.get_api_db),
) -> list[sql_api.WApiAllowed]:
    allows = sql_api.get_api_allows(db, user, domain)
    return allows
