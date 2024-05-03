from fastapi import FastAPI

from .routers import users

app = FastAPI(
    responses={
        401: {"description": "Not authorized"},
        404: {"description": "Not found"},
    },
)

app.include_router(users.router)
