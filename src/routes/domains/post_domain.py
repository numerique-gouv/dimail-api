import fastapi

from ... import auth, oxcli, sql_api, web_models
from .. import dependencies, routers


@routers.domains.post(
    "/",
    status_code=fastapi.status.HTTP_201_CREATED,
    summary="Create a domain",
    description="Create a new domain",
    response_model=web_models.Domain,
)
async def post_domain(
    db: dependencies.DependsApiDb,
    user: auth.DependsBasicAdmin,
    domain: web_models.Domain,
) -> web_models.Domain:
    if "webmail" in domain.features and domain.context_name is None:
        raise fastapi.HTTPException(
            status_code=409, detail="OX context name is mandatory for mailbox feature"
        )

    domain_db = sql_api.get_domain(db, domain.name)
    if domain_db is not None:
        raise fastapi.HTTPException(status_code=409, detail="Domain already exists")

    if "webmail" in domain.features:
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

    if "webmail" in domain.features:
        return web_models.Domain.from_db(domain_db, domain.context_name)
    else:
        return web_models.Domain.from_db(domain_db)
