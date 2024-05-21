import logging

import fastapi


class PermissionDenied(fastapi.HTTPException):
    def __init__(self):
        log = logging.getLogger(__name__)
        log.debug("Our own way to tell you you are not welcome")
        return super(PermissionDenied, self).__init__(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied",
        )
