import typing

import fastapi
import fastapi.security
import sqlalchemy.orm as orm

from .. import sql_api, web_models
from . import token


def PermissionDeniedException():
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def authenticate_user(
    db: orm.Session,
    user_name: str,
    password: str
) -> sql_api.DBUser:
    db_user = sql_api.get_api_user(db, user_name)
    if db_user is None:
        raise PermissionDeniedException()
    ok = db_user.verify_password(password)
    if not ok:
        raise PermissionDeniedException()
    return db_user


@token.get("/")
async def login_for_access_token(
    credentials: typing.Annotated[
        fastapi.security.HTTPBasicCredentials,
        fastapi.Depends(fastapi.security.HTTPBasic())
    ],
#    form_data: typing.Annotated[
#        fastapi.security.OAuth2PasswordRequestForm,
#        fastapi.Depends()
#    ],
    db: typing.Annotated[typing.Any, fastapi.Depends(sql_api.get_api_db)],
) -> web_models.WToken:
    user = authenticate_user(db, credentials.username, credentials.password)
    token = user.create_token()
    return web_models.WToken(access_token=token, token_type="bearer")

