import pathlib

import fastapi
from fastapi.middleware.cors import CORSMiddleware

from . import config, oxcli, routes, sql_api, sql_dovecot, sql_postfix

if config.settings.mode == "FAKE":
    print("Running in FAKE mode")
    for name in [ "api", "imap", "postfix" ]:
        if pathlib.Path(f"/tmp/{name}.db").is_file():
            pathlib.Path.unlink(f"/tmp/{name}.db")
    config.settings.api_db_url = "sqlite:////tmp/api.db"
    config.settings.imap_db_url = "sqlite:////tmp/imap.db"
    config.settings.postfix_db_url = "sqlite:////tmp/postfix.db"
    config.settings.ox_ssh_url = "FAKE"

engine_api = sql_api.init_db(config.settings.api_db_url)
engine_dovecot = sql_dovecot.init_db(config.settings.imap_db_url)
engine_postfix = sql_postfix.init_db(config.settings.postfix_db_url)

oxcli.declare_cluster("default", config.settings.ox_ssh_url, [])
oxcli.set_default_cluster("default")

if config.settings.mode == "FAKE":
    print("Creating the tables in the databases")
    sql_api.Api.metadata.create_all(engine_api)
    sql_dovecot.Dovecot.metadata.create_all(engine_dovecot)
    sql_postfix.Postfix.metadata.create_all(engine_postfix)

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


app.include_router(routes.routers.users)
app.include_router(routes.routers.domains)
app.include_router(routes.routers.allows)
app.include_router(routes.routers.token)
app.include_router(routes.routers.mailboxes)
app.include_router(routes.routers.aliases)


