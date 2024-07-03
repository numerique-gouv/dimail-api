# ruff: noqa: E402

import fastapi

domains = fastapi.APIRouter(
    prefix="/domains",
    tags=["domains"],
)

mailboxes = fastapi.APIRouter(
    prefix="/domains/{domain_name}/mailboxes",
    tags=["mailboxes"]
)

aliases = fastapi.APIRouter(
    prefix="/domains/{domain_name}/aliases",
    tags=["aliases"]
)

token = fastapi.APIRouter(
    prefix="/token",
    tags=["token"],
)

users = fastapi.APIRouter(
    prefix="/users",
    tags=["admin users"],
)

allows = fastapi.APIRouter(
    prefix="/allows",
    tags=["admin allows"],
)

