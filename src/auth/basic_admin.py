import logging
import typing

import fastapi
import sqlalchemy.orm as orm

from .. import sql_api
from .basic_user import BasicUser, PermissionDeniedException


class BasicAdmin(BasicUser):
    def __init__(self):
        super(BasicAdmin, self).__init__()

    async def __call__(self, request: fastapi.Request):
        log = logging.getLogger(__name__)
        user: sql_api.DBUser
        try:
            user = await super(BasicAdmin, self).__call__(request).__anext__()
        except Exception as e:
            log.info(f"Failed super with exception {e}, so failed auth.")
            raise e
        if not user:
            log.info("There is no user, failed auth.")
            raise PermissionDeniedException()
        if not user.is_admin:
            log.error("This user is not an admin. Failed auth.")
            raise PermissionDeniedException()
        yield user

DependsBasicAdmin = typing.Annotated[sql_api.DBUser, fastapi.Depends(BasicAdmin()) ]

