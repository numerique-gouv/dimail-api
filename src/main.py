from fastapi import FastAPI
import src.admin_routes
import src.routes

app = FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.include_router(src.admin_routes.users)
app.include_router(src.admin_routes.domains)
app.include_router(src.admin_routes.allows)

app.include_router(src.routes.oxusers)
