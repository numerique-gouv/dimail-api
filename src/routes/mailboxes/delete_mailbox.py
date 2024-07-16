import logging

import fastapi

from ... import auth, oxcli, sql_api, sql_dovecot
from .. import dependencies, routers

@routers.mailboxes.delete("/{user_name}", status_code=204)
async def delete_mailbox(
    domain_name: str,
    user_name: str,
    user: auth.DependsTokenUser,
    imap: dependencies.DependsDovecotDb,
    api: dependencies.DependsApiDb,
) -> None:
    """Deletes a mailbox.

    Args:
        domain_name (str): Domain name
        user_name (str): User name
        user (auth.DependsTokenUser): User credentials
        imap (dependencies.DependsDovecotDb): Dovecot database session
        api (dependencies.DependsApiDb): API database session

    Returns:
        None: No content

    Raises:
        fastapi.HTTPException: Permission denied
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: Feature 'mailbox' not available on the domain
        fastapi.HTTPException: Mailbox not found

    See Also:
        * https://fastapi.tiangolo.com/tutorial/path-params
        * https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt
        * https://fastapi.tiangolo.com/tutorial/security/simple-verify-token

    Dependencies:
        auth.DependsTokenUser
        dependencies.DependsApiDb
        dependencies.DependsDovecotDb
        oxcli
        sql_api.get_domain
        sql_dovecot.delete_user
        sql_dovecot.get_user
    """
    log = logging.getLogger(__name__)
    email = f"{user_name}@{domain_name}"
    log.info(f"Nous supprimons {email}")
    perms = user.get_creds()

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for current user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    domain_db = sql_api.get_domain(api, domain_name)
    if domain_db is None:
        log.info(f"Domain not found in database {domain_name}")
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    if "mailbox" not in domain_db.features:
        log.info(f"Missing feature 'mailbox' on domain {domain_name}")
        raise fastapi.HTTPException(
            status_code=422,
            detail="Feature 'mailbox' not available on the domain"
        )

    db_user = sql_dovecot.get_user(imap, user_name, domain_name)
    if db_user is None:
        log.info(f"La boite {user_name} n'existe pas pour le domain {domain_name}")
        raise fastapi.HTTPException(status_code=404, detail="Mailbox not found")

    ox_user = None
    if "webmail" in domain_db.features:
        ox_cluster = oxcli.OxCluster()
        ctx = ox_cluster.get_context_by_domain(domain_name)

        if ctx is None:
            log.info("Aucun contexte ne gère le domaine chez OX")
            raise fastapi.HTTPException(status_code=404, detail="Domain not found in open-xchange")

        ox_user = ctx.get_user_by_email(email)

        if ox_user is None:
            log.info("Le contexte OX ne connait pas cet email")
            raise fastapi.HTTPException(status_code=404, detail="Mailbox not found in open-xchange")

    sql_dovecot.delete_user(imap, user_name, domain_name)
    if "webmail" in domain_db.features:
        ox_user.delete()
    return None

