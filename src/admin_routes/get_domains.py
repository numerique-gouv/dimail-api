import fastapi

from .. import sql_api, web_models
from . import depends_api_db, domains


@domains.get("/")
async def get_domains(
    db=fastapi.Depends(depends_api_db),
) -> list[web_models.WDomain]:
    domains = sql_api.get_api_domains(db)
    return domains
