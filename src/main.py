import fastapi
from fastapi.middleware.cors import CORSMiddleware

from . import admin_routes, config, oxcli, routes, sql_api, sql_dovecot, sql_postfix

sql_api.init_db(config.settings.api_db_url)
sql_dovecot.init_db(config.settings.imap_db_url)
sql_postfix.init_db(config.settings.postfix_db_url)

oxcli.declare_cluster("default", config.settings.ox_ssh_url, [])
oxcli.set_default_cluster("default")

if config.settings.JWT_SECRET == "bare secret":
    raise Exception("please configure JWT_SECRET")

app = fastapi.FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(admin_routes.users)
app.include_router(admin_routes.domains)
app.include_router(admin_routes.allows)

app.include_router(routes.domains)
app.include_router(routes.token)
app.include_router(routes.mailboxes.router)
app.include_router(routes.aliases.router)
