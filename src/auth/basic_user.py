import logging
import typing

import fastapi
import fastapi.security
import sqlalchemy.orm as orm

from .. import sql_api
from . import err


def authenticate_user(db: orm.Session, user_name: str, password: str) -> sql_api.DBUser:
    """Fetch a user from the API db, checks their password, if everything
    is fine, returns the user. Will raise a PermissionDenied exception
    if something is wrong.
    May forge an admin user if the API db is empty."""
    log = logging.getLogger(__name__)
    db_user = sql_api.get_user(db, user_name)
    if db_user is None:
        log.info(f"No user found in database for username {user_name}")
        nb_users = sql_api.count_users(db)
        if nb_users == 0:
            log.info("Database is empty, forging a fake admin user for setup")
            db_user = sql_api.DBUser(name="FAKE", is_admin=True)
            return db_user
        raise err.PermissionDenied()
    ok = db_user.verify_password(password)
    if not ok:
        log.info("Wrong password")
        raise err.PermissionDenied()
    return db_user


class BasicUser(fastapi.security.HTTPBasic):
    """BasicUser is a fastapi.security.HTTPBasic that will authenticate a user"""
    def __init__(self):
        super(BasicUser, self).__init__()

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.debug("Trying to auth a user with basic http")
        creds: fastapi.security.HTTPBasicCredentials
        try:
            creds = await super(BasicUser, self).__call__(request)
        except Exception as e:
            log.info(f"Failed with exception <{e}>, so failed auth.")
            raise e
        # On utilise les valeurs par défaut de HTTPBasic, donc auto_error = True,
        # donc s'il n'y a pas de crédentials dans la requête, c'est le module de
        # base qui va lever une exception.
        # Donc, la variable creds est forcément définie.
        assert creds
        # if not creds:
        #    log.info("No credentials provided, failed auth.")
        #    raise err.PermissionDenied()

        maker = sql_api.get_maker()
        session = maker()
        try:
            user = authenticate_user(session, creds.username, creds.password)
        except Exception as e:
            log.debug("Failed auth")
            session.close()
            raise e
        try:
            log.debug(f"Greetings user {user.name}")
            yield user
        finally:
            session.close()


DependsBasicUser = typing.Annotated[sql_api.DBUser, fastapi.Depends(BasicUser())]
