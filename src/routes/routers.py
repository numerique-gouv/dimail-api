# ruff: noqa: E402
"""Routers for the FastAPI application.

This module contains the routers for the FastAPI application. Each router is
responsible for a specific set of routes. The routers are then added to the
FastAPI application in the main module.

Attributes:
    domains (fastapi.APIRouter): The router for domain routes.
    mailboxes (fastapi.APIRouter): The router for mailbox routes.
    aliases (fastapi.APIRouter): The router for alias routes.
    token (fastapi.APIRouter): The router for token routes.
    users (fastapi.APIRouter): The router for admin user routes.
    allows (fastapi.APIRouter): The router for admin allow routes.
"""
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

