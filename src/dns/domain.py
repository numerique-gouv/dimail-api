import logging

import dns.name
import dns.resolver
import sqlalchemy.orm as orm

from .. import sql_api, sql_postfix
from . import dkim, utils

# Ce qu'on cherche à valider sur un domaine :
# - est-ce que c'est vraiment un nom de domaine (i.e. pas le nom de ma belle mère)
# x est-ce que le domaine existe (intéroger NOS dns), quels sont les DNS
#   faisant autorité
# - quels sont les entrées attendues (SPF, divers CNAME, clef DKIM) -> lister
#   les enregistrements à vérifier
# x vérifier chacun de ces enregistrements sur un des dns faisant aurotité (en
#   court-circuitant le cache)
# - refaire les mêmes contrôles sur nos dns et/ou sur des dns publics, indiquer
#   si les caches sont à jour ou s'il y a une propagation en cours
# x produire des messages d'erreur explicites sur ce qui ne va pas et ce qu'il
#   faut corriger
required_mx = "mx.ox.numerique.gouv.fr."
required_spf = "include:_spf.ox.numerique.gouv.fr"

targets = {
    "webmail": "webmail.ox.numerique.gouv.fr.",
    "imap": "imap.ox.numerique.gouv.fr.",
    "mail": "mail.ox.numerique.gouv.fr.",
    "smtp": "smtp.ox.numerique.gouv.fr.",
}
#required_mx = "mx.fdn.fr."


class Domain:
    def __init__(
        self,
        domain: sql_api.DBDomain,
    ):
        self.domain = domain
        self.dest_domain = domain.get_mailbox_domain()
        self.dest_name = dns.name.from_text(self.dest_domain)
        self.valid = None
        self.errs = []
        self.resolvers = {}
        if domain.dkim_selector is not None:
            self.dkim_domain = domain.dkim_selector + "._domainkey." + self.dest_domain
            self.dkim_name = dns.name.from_text(self.dkim_domain)

    def add_err(self, test: str, err: str, detail: str = ""):
        self.errs.append({"test": test, "code": err, "detail": detail})
        self.valid = False

    def get_auth_resolver(self, domain: str, insist: bool = False) -> dns.resolver.Resolver:
        if domain in self.resolvers:
            return self.resolvers[domain]
        try:
            self.resolvers[domain] = utils.make_auth_resolver(domain, insist)
        except Exception:
            return None
        return self.resolvers[domain]

    def check_exists(self):
        resolver = self.get_auth_resolver(self.domain.name)
        if resolver is None:
            self.add_err("domain_exist", "must_exist", f"Le domaine {self.domain.name} n'existe pas")
            return

    def try_cname_for_mx(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            answer = resolver.resolve(self.dest_name, rdtype = "CNAME")
            self.dest_domain = str(answer[0].target)
            print(f"Je trouve un CNAME vers {self.dest_domain}, je le prend comme dest_domain")
            self.dest_name = dns.name.from_text(self.dest_domain)
            return self.check_mx()
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            self.add_err("mx", "no_mx", "Il n'y a pas d'enregistrement MX ou CNAME sur le domaine")
            return
        except Exception as e:
            print(f"Unexpected exception while searching for a CNAME for a MX : {e}")
            raise

    def check_mx(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            print(f"Je cherche un MX pour {self.dest_domain}")
            answer = resolver.resolve(self.dest_name, rdtype = "MX")
        except dns.resolver.NXDOMAIN:
            print("NXDOMAIN")
            self.add_err("mx", "no_mx", "Il n'y a pas d'enregistrement MX sur le domaine")
            return
        except dns.resolver.NoAnswer:
            return self.try_cname_for_mx()
        except Exception as e:
            print(f"Unexpected exception while searching for MX {e}")
            raise

        nb_mx = len(answer)
        if nb_mx != 1 and False:
            self.add_err("mx", "one_mx", f"Je veux un seul MX, et j'en trouve {nb_mx}")
            return
        mx = str(answer[0].exchange)
        if not mx == required_mx:
            self.add_err(
                "mx",
                "wrong_mx", 
                f"Je veux que le MX du domaine soit {required_mx}, "
                f"or je trouve {mx}"
            )
            return

    def check_cname(self, name):
        if hasattr(self.domain, name+"_domain"):
            if getattr(self.domain, name+"_domain") is None:
                origins = [ name + "." + self.domain.name ]
            else:
                origins = [ getattr(self.domain, name+"_domain") ]
        else:
            if hasattr(self.domain, name+"_domains"):
                if getattr(self.domain, name+"_domains") is None:
                    origins = [ name + "." + self.domain.name ]
                else:
                    origins = getattr(self.domain, name+"_domains")

        target = targets[name]
        for origin in origins:
            resolver = self.get_auth_resolver(origin)
            if resolver is None:
                self.add_err(f"cname_{name}", f"no_cname_{name}", f"Il faut un CNAME {origin} qui renvoie vers {target}")
                continue
            try:
                answer = resolver.resolve(origin, rdtype = "CNAME")
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                self.add_err(f"cname_{name}", f"no_cname_{name}", f"Il n'y a pas de CNAME {origin} -> {target}")
                continue
            except Exception as e:
                print(f"Unexpected exception when searching for a CNAME : {e}")
                raise
            got_target = str(answer[0].target)
            if not got_target == target:
                self.add_err(
                    f"cname_{name}",
                    f"wrong_cname_{name}",
                    f"Le CNAME pour {origin} n'est pas bon, "
                    f"il renvoie vers {got_target} et je veux {target}"
                )

    def check_spf(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            answer = resolver.resolve(self.dest_name, rdtype="TXT")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            answer = []
        except Exception as e:
            print(f"Unexpected exception when searching for the SPF record : {e}")
            raise
        found_spf = False
        valid_spf = False
        for item in answer:
            txt = str(item)
            if txt.startswith("\"v=spf1 "):
                found_spf = True
                if required_spf in txt:
                    valid_spf = True
                    return
        if not found_spf:
            self.add_err("spf", "no_spf", f"Il faut un SPF record, et il doit contenir {required_spf}")
            return
        if not valid_spf:
            self.add_err("spf", "wrong_spf", f"Le SPF record ne contient pas {required_spf}")
            return

    def check_dkim(self):
        if self.domain.dkim_selector is None:
            print("Je ne peux pas controler la clef DKIM du domaine.")
            return
        resolver = self.get_auth_resolver(self.dkim_domain, True)
        try:
            answer = resolver.resolve(self.dkim_name, rdtype="TXT")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            answer = []
        except Exception as e:
            print(f"Unexpected exception when searching for the DKIM record : {e}")
            raise
        found_dkim = False
        valid_dkim = False
        want_dkim = dkim.DkimInfo(self.domain.dkim_public)
        for item in answer:
            txt = str(item)
            if txt.startswith("\"v=DKIM1; "):
                found_dkim = True
                got_dkim = dkim.DkimInfo(txt)
                if want_dkim == got_dkim:
                    valid_dkim = True
                    return
        if not found_dkim:
            self.add_err("dkim", "no_dkim", "Il faut un DKIM record, et il doit contenir la bonne clef")
            return
        if not valid_dkim:
            self.add_err("dkim", "wrong_dkim", "Le DKIM record n'est pas valide (il ne contient pas la bonne clef)")
            return

    def _check_domain(self) -> bool:
        print(f"Je check le domain {self.domain.name}")
        self.valid = True
        self.check_exists()
        if not self.valid:
            return
        self.check_mx()
        if self.domain.has_feature("webmail"):
            self.check_cname("webmail")
        if self.domain.has_feature("mailbox"):
            self.check_cname("imap")
        self.check_cname("smtp")
        self.check_spf()
        self.check_dkim()

    def check(self):
        if self.valid is None:
            self._check_domain()
        print(f"Le domain {self.domain.name} est valide: {self.valid}")
        if len(self.errs) > 0:
            print("Les erreurs:")
            for err in self.errs:
                print(f"- {err}")
        print("")

    def db_setup(self, db: orm.Session):
        if self.domain.has_feature("mailbox"):
            # Je veux être présent dans mailbox_domain, avec la bonne valeur
            dom = sql_postfix.get_mailbox_domain(db, self.domain.name)
            if dom is not None:
                if not dom.mailbox_domain == self.domain.get_mailbox_domain():
                    sql_postfix.delete_mailbox_domain(db, self.domain.name)
                    dom = None
            if dom is None:
                dom = sql_postfix.create_mailbox_domain(db, self.domain.name, self.domain.get_mailbox_domain())
            # Je veux être absent dans alias_domain
            dom = sql_postfix.get_alias_domain(db, self.domain.name)
            if dom is not None:
                sql_postfix.delete_alias_domain(db, self.domain.name)
        elif self.domain.has_feature("alias"):
            # Je veux être absent dans mailbox_domain
            dom = sql_postfix.get_mailbox_domain(db, self.domain.name)
            if dom is not None:
                sql_postfix.delete_mailbox_domain(db, self.domain.name)
            # Je veux être présent dans alias_domain, avec la bonne valeur
            dom = sql_postfix.get_alias_domain(db, self.domain.name)
            if dom is not None:
                if not dom.alias_domain == self.domain.get_alias_domain():
                    sql_postfix.delete_alias_domain(db, self.domain.name)
                    dom = None
            if dom is None:
                dom = sql_postfix.create_alias_domain(db, self.domain.name, self.domain.get_alias_domain())


def foreground_check_domain(db: orm.Session, db_dom: sql_api.DBDomain) -> sql_api.DBDomain:
    name = db_dom.name
    ck_dom = Domain(db_dom)
    ck_dom.check()
    sql_api.update_domain_dtchecked(db, name, "now")
    if ck_dom.valid:
        sql_api.update_domain_state(db, name, "ok")
        db_dom = sql_api.update_domain_errors(db, name, None)
    else:
        sql_api.update_domain_state(db, name, "broken")
        db_dom = sql_api.update_domain_errors(db, name, ck_dom.errs)
    return db_dom

def background_check_new_domain(name: str):
    log = logging.getLogger(__name__)
    maker = sql_api.get_maker()
    db = maker()
    db_dom = sql_api.get_domain(db, name)
    if db_dom is None:
        log.error("Je ne sais pas vérifier un domaine qui n'existe pas en base")
        db.close()
        return
    db_dom = foreground_check_domain(db, db_dom)
    db.close()
