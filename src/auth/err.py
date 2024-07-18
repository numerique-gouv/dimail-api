
import fastapi


class PermissionDenied(fastapi.HTTPException):
    """Permission denied error as fastapi.HTTPException

    This error is raised when a user tries to access a resource
    that they do not have permission to access.

    See also:
    - https://fastapi.tiangolo.com/tutorial/handling-errors/

    Example:
    ```python
    from fastapi import FastAPI
    from .auth import err

    app = FastAPI()

    @app.get("/items/{item_id}")
    async def read_item(item_id: int):
        if item_id == 1:
            raise err.PermissionDenied()
        return {"item_id": item
    ```
    """
    def __init__(self):
        super(PermissionDenied, self).__init__(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
