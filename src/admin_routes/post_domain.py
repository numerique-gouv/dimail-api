import fastapi

from .. import auth, oxcli, sql_api, web_models
from . import DependsApiDb, domains


@domains.post("/", status_code=201)
async def post_domain(
    db: DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain: web_models.WDomain,
) -> web_models.WDomain:
    if "webmail" in domain.features and domain.context_name is None:
        raise fastapi.HTTPException(
            status_code=409, detail="OX context name is mandatory for mailbox feature"
        )

    domain_db = sql_api.get_domain(db, domain.name)
    if domain_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="Domain already exists")

    ox_cluster = oxcli.OxCluster()
    ctx = ox_cluster.get_context_by_domain(domain.name)
    if ctx is not None and ctx.name != domain.context_name:
        raise fastapi.HTTPException(
            status_code=409,
            detail=f"The domain is currently mapped to OX context {ctx.name}",
        )

    if ctx is None:
        ctx = ox_cluster.get_context_by_name(domain.context_name)
        if ctx is None:
            ctx = ox_cluster.create_context(None, domain.context_name, domain.name)
        else:
            ctx.add_mapping(domain.name)

    domain_db = sql_api.create_domain(
        db,
        name=domain.name,
        features=domain.features,
        webmail_domain=domain.webmail_domain,
        mailbox_domain=domain.mailbox_domain,
        imap_domains=domain.imap_domains,
        smtp_domains=domain.smtp_domains,
    )

    return web_models.WDomain.from_db(domain_db, ctx.name)
