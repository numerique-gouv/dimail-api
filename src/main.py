import fastapi

from . import admin_routes, config, routes, sql_api, sql_dovecot

sql_api.init_db(config.settings.api_db_url)
sql_dovecot.init_db(config.settings.imap_db_url)

if config.settings.JWT_SECRET == "bare secret":
    raise Exception("please configure JWT_SECRET")

app = fastapi.FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.include_router(admin_routes.users)
app.include_router(admin_routes.domains)
app.include_router(admin_routes.allows)

app.include_router(routes.token)
app.include_router(routes.mailboxes)
