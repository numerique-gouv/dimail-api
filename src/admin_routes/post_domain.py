from fastapi import Depends, HTTPException
import src.sql_api
from . import domains

@domains.post(
  '/'
)
async def post_domain(
    domain: src.sql_api.WApiDomain,
    db = Depends(src.sql_api.get_api_db),
) -> src.sql_api.WApiDomain:

    domain_db = src.sql_api.get_api_domain(db, domain.name)

    if domain_db is not None:
        raise HTTPException(status_code=409, detail='Domain already exists')

    return src.sql_api.create_api_domain(db, domain)


