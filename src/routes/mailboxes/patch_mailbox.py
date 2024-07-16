import logging

import fastapi

from ... import auth, oxcli, sql_api, sql_dovecot, web_models
from .. import dependencies, routers

@routers.mailboxes.patch("/{user_name}", status_code=200)
async def patch_mailbox(
    domain_name: str,
    user_name: str,
    updates: web_models.UpdateMailbox,
    user: auth.DependsTokenUser,
    imap: dependencies.DependsDovecotDb,
    api: dependencies.DependsApiDb,
) -> web_models.Mailbox:
    """Updates a mailbox. All the fields are optional and are the information
    to update on that mailbox. Some updates are not yet implemented.

    Args:
        domain_name (str): Domain name
        user_name (str): Mailbox username
        updates (web_models.UpdateMailbox): Mailbox information to update
        user (auth.DependsTokenUser): User credentials
        imap (dependencies.DependsDovecotDb): Dovecot database session
        api (dependencies.DependsApiDb): API database session

    Returns:
        web_models.Mailbox: Updated mailbox information

    Raises:
        fastapi.HTTPException: Permission denied
        fastapi.HTTPException: Domain not found
        fastapi.HTTPException: Feature 'mailbox' not available on the domain
        fastapi.HTTPException: Mailbox not found
        fastapi.HTTPException: Not yet implemented

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
        sql_dovecot.get_user
        web_models.Mailbox.from_both_users
    """
    log = logging.getLogger(__name__)
    email = f"{user_name}@{domain_name}"
    log.info(f"Nous modifions {email}")
    perms = user.get_creds()
    log.info(f"Nous avons comme permissions: {perms}")

    if not perms.can_read(domain_name):
        log.info(f"Permission denied on domain {domain_name} for current user")
        raise fastapi.HTTPException(status_code=403, detail="Permission denied")

    domain_db = sql_api.get_domain(api, domain_name)
    if domain_db is None:
        log.info(f"Domain not found in database {domain_name}")
        raise fastapi.HTTPException(status_code=404, detail="Domain not found")

    if updates.domain is not None:
        if not perms.can_read(updates.domain):
            log.info(f"Permission denied on target domain {updates.domain} for current user")
            raise fastapi.HTTPException(status_code=403, detail="Permission denied")

        new_domain_db = sql_api.get_domain(api, updates.domain)
        if new_domain_db is None:
            log.info(f"Target domain not found in database {updates.domain}")
            raise fastapi.HTTPException(status_code=404, detail="Target domain not found")

        log.error("Le deplacement d'une mailbox d'un domaine a l'autre n'est pas encore possible")
        raise fastapi.HTTPException(status_code=422, detail="Not yet implemented")

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

    if updates.user_name is not None:
        log.error("Le renommage d'une mailbox n'est pas encore possible")
        raise fastapi.HTTPException(status_code=422, detail="Not yet implemented")

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

        changes = {}
        if updates.givenName is not None:
            changes["givenName"] = updates.givenName

        if updates.surName is not None:
            changes["surName"] = updates.surName

        if updates.displayName is not None:
            changes["displayName"] = updates.displayName

        ox_user.change(**changes)
        ox_user = ctx.get_user_by_email(email)

    return web_models.Mailbox.from_both_users(ox_user, db_user, "webmail" in domain_db.features)

