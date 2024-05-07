import fastapi

from .. import sql_api
from . import domains


@domains.get("/")
async def get_domains(
    db=fastapi.Depends(sql_api.get_api_db),
) -> list[sql_api.WApiDomain]:
    domains = sql_api.get_api_domains(db)
    return domains
