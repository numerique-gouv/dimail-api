import typing

import fastapi
import fastapi.security
import sqlalchemy.orm as orm

from .. import sql_api


def PermissionDeniedException():
    return fastapi.HTTPException(
        status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        detail="Permission denied",
        headers={"WWW-Authenticate": "Bearer"},
    )


def authenticate_user(db: orm.Session, user_name: str, password: str) -> sql_api.DBUser:    
    log = logging.getLogger(__name__)
    db_user = sql_api.get_api_user(db, user_name)
    if db_user is None:
        log.info("No user found in database for username {user_name}")
        nb_users = sql_api.nb_users(db)
        if nb_users == 0:
            log.info("Database is empty, forging a fake admin user for setup")
            db_user = sql_api.DBUser(name="FAKE", is_admin=True)
            return db_user
        raise PermissionDeniedException()
    ok = db_user.verify_password(password)
    if not ok:
        log.info("Wrong password")
        raise PermissionDeniedException()
    return db_user

import logging
class BasicUser(fastapi.security.HTTPBasic):
    def __init__(self):
        super(BasicUser, self).__init__()

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.info("We are in da place")
        creds: fastapi.security.HTTPBasicCredentials
        try:
            creds = await super(BasicUser, self).__call__(request)
        except Exception as e:
            log.info(f"Failed super with exception <{e}>, so failed auth.")
            raise e
        if not creds:
            log.info("No credentials provided, failed auth.")
            raise PermissionDeniedException()
        
        maker = sql_api.get_maker()
        session = maker()
        user = authenticate_user(session, creds.username, creds.password)
        try:
            log.info(f"Gretting user {user.name}")
            yield user
        finally:
            session.close()

DependsBasicUser = typing.Annotated[sql_api.DBUser, fastapi.Depends(BasicUser()) ]

