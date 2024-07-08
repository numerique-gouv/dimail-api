import logging

import fastapi


class PermissionDenied(fastapi.HTTPException):
    def __init__(self):
        super(PermissionDenied, self).__init__(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
