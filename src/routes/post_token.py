import datetime
import typing

import fastapi.security
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from .. import config, sql_api, web_models
from . import token


def PermissionDeniedException():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def authenticate_user(
    db: Session, user_name: str, password: str
) -> sql_api.DBUser | bool:
    db_user = sql_api.get_api_user(db, user_name)
    if db_user is None:
        raise PermissionDeniedException()
    ok = sql_api.verify_password(password, db_user.hashed_password)
    if not ok:
        return False
    return db_user


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            minutes=15
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.settings["JWT_SECRET"], algorithm="HS256"
    )
    return encoded_jwt


def get_api_db():
    api_db = sql_api.get_api_db()
    return next(api_db)


# TODO: post -> get + basic auth
@token.post("/")
async def login_for_access_token(
    form_data: typing.Annotated[fastapi.security.OAuth2PasswordRequestForm, Depends()],
    db: typing.Annotated[typing.Any, fastapi.Depends(get_api_db)],
) -> web_models.WToken:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise PermissionDeniedException()
    access_token_expires = datetime.timedelta(minutes=47)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )
    return web_models.WToken(access_token=access_token, token_type="bearer")
