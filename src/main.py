import fastapi

import src.admin_routes
import src.routes

import src.config
import src.sql_api

src.sql_api.init_api_db(src.config.settings.api_db_url)

app = fastapi.FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.include_router(src.admin_routes.users)
app.include_router(src.admin_routes.domains)
app.include_router(src.admin_routes.allows)

app.include_router(src.routes.oxusers)
