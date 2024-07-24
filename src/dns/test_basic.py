import pytest

from .. import sql_api
from . import dkim
from . import domain

def test_dkim(log):
    with pytest.raises(Exception):
        info = dkim.DkimInfo("\"coin=pan; v=DKIM1; h=toto\"")

    info = dkim.DkimInfo("\"v=DKIM1; h=sha256; k=rsa; p=coincoin\"")
    assert isinstance(info, dkim.DkimInfo)
    assert info.v == "DKIM1"
    assert info.h == "sha256"
    assert info.k == "rsa"
    assert info.p == "coincoin"

def test_domain_check():
    db_dom = sql_api.DBDomain(
        name = "fdn.fr",
        features = [ "webmail", "mailbox" ],
    )
    domain.Domain(db_dom).check()

    db_dom = sql_api.DBDomain(
        name = "coincoin",
        features=["webmail", "mailbox"],
    )
    domain.Domain(db_dom).check()

    db_dom = sql_api.DBDomain(
        name = "La tête à l'envers",
        features = ["mailbox"],
    )
    domain.Domain(db_dom).check()

    db_dom = sql_api.DBDomain(
        name="mail.numerique.gouv.fr",
        features=["webmail", "mailbox"],
        webmail_domain="webmail.numerique.gouv.fr",
        imap_domains=["imap.numerique.gouv.fr"],
        smtp_domains=["smtp.numerique.gouv.fr"],
        mailbox_domain="mail.numerique.gouv.fr",
    )

    domain.Domain(db_dom,
        dkim = """"v=DKIM1; h=sha256; k=rsa; "
                "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR"
                "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
                "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
                "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
                "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
                "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
                "LwIDAQAB"
        """
    ).check()


