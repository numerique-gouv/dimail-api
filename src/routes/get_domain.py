import fastapi
from .. import auth, sql_api, web_models
from . import DependsApiDb, domains
import logging


@domains.get("/{domain_name}")
async def get_domain(
    db: DependsApiDb,
    user: auth.DependsTokenUser,
    domain_name: str,
) -> web_models.Domain:
    log = logging.getLogger(__name__)
    perms = user.get_creds()

    domain_db = sql_api.get_domain(db, domain_name)
    if domain_db is None:
        log.info(f"Domain {domain_name} not found.")
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for user.")
        raise fastapi.HTTPException(status_code=401, detail="Not authorized.")

    return web_models.Domain.from_db(domain_db)
