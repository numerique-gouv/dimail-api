import fastapi

from . import admin_routes
from . import routes

from . import config
from . import sql_api
from . import sql_dovecot

sql_api.init_api_db(config.settings.api_db_url)
sql_dovecot.init_dovecot_db(config.settings.imap_db_url)

app = fastapi.FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.include_router(admin_routes.users)
app.include_router(admin_routes.domains)
app.include_router(admin_routes.allows)

app.include_router(routes.mailboxes)
