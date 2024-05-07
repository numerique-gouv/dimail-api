from fastapi import Depends, HTTPException

import src.sql_api

from . import allows


@allows.post("/")
async def post_allow(
    allow: src.sql_api.WApiAllowed,
    db=Depends(src.sql_api.get_api_db),
) -> src.sql_api.WApiAllowed:
    user_db = src.sql_api.get_api_user(db, allow.user)
    if user_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    domain_db = src.sql_api.get_api_domain(db, allow.domain)
    if domain_db is None:
        raise HTTPException(status_code=404, detail="Domain not found")
    allowed_db = src.sql_api.get_api_allowed(db, allow.user, allow.domain)
    if allowed_db is not None:
        raise HTTPException(
            status_code=409, detail="Domain already allowed for this user"
        )
    return src.sql_api.allow_domain_for_user(db, allow)
