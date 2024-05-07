from fastapi import Depends

import src.sql_api

from . import domains


@domains.get("/")
async def get_domains(
    db=Depends(src.sql_api.get_api_db),
) -> list[src.sql_api.WApiDomain]:
    domains = src.sql_api.get_api_domains(db)
    return domains
