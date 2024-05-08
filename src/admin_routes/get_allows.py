from typing import Optional

import fastapi

from .. import sql_api, web_models
from . import allows


@allows.get("/")
async def get_allows(
    user: str = "",
    domain: str = "",
    db=fastapi.Depends(sql_api.get_api_db),
) -> list[web_models.WAllowed]:

    allows = sql_api.get_api_allows(db, user, domain)
    return allows
