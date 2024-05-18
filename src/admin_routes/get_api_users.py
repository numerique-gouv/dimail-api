import fastapi

from .. import sql_api, web_models
from . import depends_api_db, ox


@ox.get("/api/users")
    db=fastapi.Depends(sql_api.get_api_db),
    db=fastapi.Depends(depends_api_db),
) -> list[web_models.WUser]:
    users = sql_api.get_api_users(db)
    return users
