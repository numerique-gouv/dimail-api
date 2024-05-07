from typing import Optional

from fastapi import Depends

import src.sql_api

from . import allows


@allows.get("/")
async def get_allows(
    user: str = "",
    domain: str = "",
    db=Depends(src.sql_api.get_api_db),
) -> list[src.sql_api.WApiAllowed]:
    allows = src.sql_api.get_api_allows(db, user, domain)
    return allows
