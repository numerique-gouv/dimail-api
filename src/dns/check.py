import dns.name
import dns.resolver
import dns.rdtypes
import dns.rdtypes.ANY.NS

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
webmail_target = "webmail.ox.numerique.gouv.fr."
imap_target = "imap.ox.numerique.gouv.fr."
mail_target = "mail.ox.numerique.gouv.fr."
smtp_target = "smtp.ox.numerique.gouv.fr."
#required_mx = "mx.fdn.fr."

def get_ip_address(domain: str) -> str:
    answer = dns.resolver.resolve(domain)
    for item in answer:
        return str(item.address)

def make_auth_resolver(domain: str, insist: bool = False) -> dns.resolver.Resolver:
    print(f"Je cherche les resolvers pour {domain}")
    name = dns.name.from_text(domain)
    try:
        answer = dns.resolver.resolve(name, rdtype = "NS")
    except dns.resolver.NoAnswer:
        (_, up) = domain.split(".", 1)
        print(f"Je ne trouve pas les NS pour {domain}, je remonte d'un cran vers {up}")
        return make_auth_resolver(up, insist)
    except dns.resolver.NXDOMAIN:
        if insist:
            (_, up) = domain.split(".", 1)
            print(f"Je ne trouve pas les NS pour {domain}, je remonte d'un cran vers {up}")
            return make_auth_resolver(up, insist)
        raise
    except Exception:
        raise
    addresses = []
    for item in answer:
        ip_addr = get_ip_address(str(item.target))
        addresses.append(ip_addr)
    resolver = dns.resolver.Resolver()
    resolver.nameservers = addresses
    return resolver

class DkimInfo:
    v: str | None
    h: str | None
    k: str | None
    p: str | None

    def __init__(self, text: str):
        if text.startswith('"'):
            text = text.replace(" ","")
            text = text.replace('"', "")
            text = text.replace("\n", "")
            text = text.replace("\t", "")
        items = text.split(";")
        for item in items:
            print(f"Je regarde l'item {item}")
            (key, val) = item.split("=", 1)
            print(f"key = '{key}' et val = '{val}'")
            setattr(self, key, val)
        if self.v is None or self.h is None or self.k is None or self.p is None:
            raise Exception("Invalid DKIM")

    def __eq__(self, other) -> bool:
        if not isinstance(other, DkimInfo):
            return False
        if self.v == other.v and self.h == other.h and self.k == other.k and self.p == other.p:
            return True
        return False

    def __str__(self) -> str:
        return f"DkimInfo(v={self.v}, h={self.h}, k={self.k}, p={self.p})"

class CheckDomain:
    def __init__(
        self,
        domain: str,
        features: list[str],
        selector: str = "mecol",
        webmail_domain: str | None = None,
        imap_domain: str | None = None,
        smtp_domain: str | None = None,
        mail_domain: str | None = None,
        dkim: str = "",
    ):
        self.domain = domain
        self.features = features
        self.name = dns.name.from_text(domain)
        self.dest_domain = domain
        self.dest_name = self.name
        self.valid = None
        self.errs = []
        self.resolvers = {}
        if webmail_domain is None:
            self.webmail_domain = "webmail." + self.domain
        else:
            self.webmail_domain = webmail_domain
        if imap_domain is None:
            self.imap_domain = "imap." + self.domain
        else:
            self.imap_domain = imap_domain
        if smtp_domain is None:
            self.smtp_domain = "smtp." + self.domain
        else:
            self.smtp_domain = smtp_domain
        if mail_domain is None:
            self.mail_domain = "mail." + self.domain
        else:
            self.mail_domain = mail_domain
        self.selector = selector
        self.dkim_domain = self.selector + "._domainkey." + self.domain
        self.dkim_name = dns.name.from_text(self.dkim_domain)

        self.dkim = dkim

    def add_err(self, err: str):
        self.errs.append(err)
        self.valid = False

    def get_auth_resolver(self, domain: str, insist: bool = False) -> dns.resolver.Resolver:
        if domain in self.resolvers:
            return self.resolvers[domain]
        try:
            self.resolvers[domain] = make_auth_resolver(domain, insist)
        except Exception:
            return None
        return self.resolvers[domain]

    def check_exists(self):
        resolver = self.get_auth_resolver(self.domain)
        if resolver is None:
            self.add_err(f"Le domaine {self.domain} n'existe pas")
            return

    def try_cname_for_mx(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            answer = resolver.resolve(self.dest_name, rdtype = "CNAME")
            self.dest_domain = str(answer[0].target)
            print(f"Je trouve un CNAME vers {self.dest_domain}, je le prend comme dest_domain")
            self.dest_name = dns.name.from_text(self.dest_domain)
            return self.check_mx()
        except dns.resolver.NXDOMAIN:
            self.add_err("Il n'y a pas d'enregistrement MX ou CNAME sur le domaine")
            return
        except Exception:
            raise

    def check_mx(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            print(f"Je cherche un MX pour {self.dest_domain}")
            answer = resolver.resolve(self.dest_name, rdtype = "MX")
        except dns.resolver.NXDOMAIN:
            self.add_err("Il n'y a pas d'enregistrement MX sur le domaine")
            return
        except dns.resolver.NoAnswer:
            return self.try_cname_for_mx()
        except Exception:
            raise

        nb_mx = len(answer)
        if nb_mx != 1 and False:
            self.add_err(f"Je veux un seul MX, et j'en trouve {nb_mx}")
            return
        mx = str(answer[0].exchange)
        if not mx == required_mx:
            self.add_err(
                f"Je veux que le MX du domaine soit {required_mx}, "
                f"or je trouve {mx}"
            )
            return

    def check_cname(self, name, target):
        resolver = self.get_auth_resolver(name)
        if resolver is None:
            self.add_err(f"Il faut un CNAME {name} qui renvoie vers {target}")
            return
        try:
            answer = resolver.resolve(name, rdtype = "CNAME")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            self.add_err(f"Il n'y a pas de CNAME {name} -> {target}")
            return
        except Exception:
            raise
        got_target = str(answer[0].target)
        if not got_target == target:
            self.add_err(
                f"Le CNAME pour {name} n'est pas bon, "
                f"il renvoie vers {got_target} et je veux {target}"
            )

    def check_spf(self):
        resolver = self.get_auth_resolver(self.dest_domain)
        try:
            answer = resolver.resolve(self.dest_name, rdtype="TXT")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            answer = []
        except Exception:
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
            self.add_err(f"Il faut un SPF record, et il doit contenir {required_spf}")
            return
        if not valid_spf:
            self.add_err(f"Le SPF record ne contient pas {required_spf}")
            return

    def check_dkim(self):
        if self.dkim == "":
            print("Je ne peux pas controler la clef DKIM du domaine.")
            return
        resolver = self.get_auth_resolver(self.dkim_domain, True)
        try:
            answer = resolver.resolve(self.dkim_name, rdtype="TXT")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            answer = []
        except Exception:
            raise
        found_dkim = False
        valid_dkim = False
        want_dkim = DkimInfo(self.dkim)
        for item in answer:
            txt = str(item)
            if txt.startswith("\"v=DKIM1; "):
                found_dkim = True
                got_dkim = DkimInfo(txt)
                if want_dkim == got_dkim:
                    valid_dkim = True
                    return
        if not found_dkim:
            self.add_err("Il faut un DKIM record, et il doit contenir la bonne clef")
            return
        if not valid_dkim:
            self.add_err("Le DKIM record n'est pas valide (il ne contient pas la bonne clef)")
            return

    def _check_domain(self) -> bool:
        print(f"Je check le domain {self.domain}")
        self.valid = True
        self.check_exists()
        if not self.valid:
            return
        self.check_mx()
        if "webmail" in self.features:
            self.check_cname(self.webmail_domain, webmail_target)
        if "mailbox" in self.features:
            self.check_cname(self.imap_domain, imap_target)
        self.check_cname(self.mail_domain, mail_target)
        self.check_cname(self.smtp_domain, smtp_target)
        self.check_spf()
        self.check_dkim()

    def check_domain(self):
        if self.valid is None:
            self._check_domain()
        print(f"Le domain {self.domain} est valide: {self.valid}")
        if len(self.errs) > 0:
            print("Les erreurs:")
            for err in self.errs:
                print(f"- {err}")
        print("")


CheckDomain("fdn.fr", features=["webmail", "mailbox"]).check_domain()
CheckDomain("coincoin", features=["webmail", "mailbox"]).check_domain()
CheckDomain("La tête à l'envers", features=["mailbox"]).check_domain()
CheckDomain(
    domain="mail.numerique.gouv.fr",
    features=["webmail", "mailbox"],
    webmail_domain="webmail.numerique.gouv.fr",
    imap_domain="imap.numerique.gouv.fr",
    smtp_domain="smtp.numerique.gouv.fr",
    mail_domain="mail.numerique.gouv.fr",
    dkim = """"v=DKIM1; h=sha256; k=rsa; "
          "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpRpsTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpHQBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFrulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
          "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxksxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlVLwIDAQAB"
    """
).check_domain()
exit(0)


