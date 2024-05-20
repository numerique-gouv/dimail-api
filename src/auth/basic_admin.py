import logging
import typing

import fastapi

from .. import sql_api
from . import err
from .basic_user import BasicUser


class BasicAdmin(BasicUser):
    def __init__(self):
        super(BasicAdmin, self).__init__()

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        log.debug("Trying to auth an ADMIN with basic http")
        user: sql_api.DBUser
        try:
            user = await super(BasicAdmin, self).__call__(request).__anext__()
        except Exception as e:
            log.info(f"Failed super with exception {e}, so failed auth.")
            raise e
        if not user:
            log.info("There is no user, failed auth.")
            raise err.PermissionDenied()
        if not user.is_admin:
            log.error("This user is not an admin. Failed auth.")
            raise err.PermissionDenied()
        yield user


DependsBasicAdmin = typing.Annotated[sql_api.DBUser, fastapi.Depends(BasicAdmin())]
