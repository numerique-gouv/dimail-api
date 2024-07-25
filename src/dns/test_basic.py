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
        name = "La tête à l'envers",
        features = ["mailbox"],
    )
    ck_dom = domain.Domain(db_dom)
    ck_dom.check()
    assert ck_dom.valid is False
    assert len(ck_dom.errs) == 1
    assert ck_dom.errs[0]["code"] == "must_exist"

    db_dom = sql_api.DBDomain(
        name = "fdn.fr",
        features = [ "webmail", "mailbox" ],
    )
    ck_dom = domain.Domain(db_dom)
    ck_dom.check()
    assert ck_dom.valid is False
    assert len(ck_dom.errs) == 6
    codes = [ err["code"] for err in ck_dom.errs ]
    assert "wrong_mx" in codes
    assert "wrong_cname_webmail" in codes
    assert "wrong_cname_imap" in codes
    assert "no_cname_mailbox" in codes
    assert "no_cname_smtp" in codes
    assert "wrong_spf" in codes

    db_dom = sql_api.DBDomain(
        name = "coincoin",
        features=["webmail", "mailbox"],
    )
    ck_dom = domain.Domain(db_dom)
    ck_dom.check()
    assert ck_dom.valid is False
    assert len(ck_dom.errs) == 1
    codes = [ err["code"] for err in ck_dom.errs ]
    assert "must_exist" in codes

    db_dom = sql_api.DBDomain(
        name="numerique.gouv.fr",
        features=["webmail", "mailbox"],
        mailbox_domain="mail.numerique.gouv.fr",
    )

    ck_dom = domain.Domain(db_dom,
        dkim = """"v=DKIM1; h=sha256; k=rsa; "
                "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR"
                "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
                "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
                "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
                "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
                "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
                "LwIDAQAB"
        """,
        selector = "mecol",
    )
    ck_dom.check()
    assert ck_dom.valid is True


