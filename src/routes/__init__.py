from fastapi import APIRouter

from .. import sql_api, sql_dovecot

mailboxes = APIRouter(prefix="/mailboxes", tags=["mailboxes"])
token = APIRouter(prefix="/token", tags=["token"])

def depends_api_db():
    maker = sql_api.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()

def depends_dovecot_db():
    maker = sql_dovecot.get_maker()
    db = maker()
    # En cas d'erreur, on va lever une exception (404, 403, etc), or il faudra
    # quand meme fermer la connexion a la base de données
    try:
        yield db
    finally:
        db.close()

from .get_mailbox import get_mailbox
from .get_mailboxes import get_mailboxes
from .post_token import login_for_access_token

# from .post_user import post_user
