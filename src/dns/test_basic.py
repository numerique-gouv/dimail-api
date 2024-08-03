import pytest

from .. import sql_api
from . import dkim
from . import domain
from . import spf
from . import utils

def test_utils():
    (dns, txt) = utils.get_txt_from_dns_record(
        "selector._domainkey.example.com\tIN TXT \t (\"x=y; a=b; p=bla\" \"blablabla; truc=chose\")"
    )
    assert dns == "selector._domainkey.example.com"
    assert txt == "\"x=y; a=b; p=bla\" \"blablabla; truc=chose\""

    txt = utils.join_text_parts("\"abcdef\" \"g\"\t \"\"\n \"hijk\"")
    assert txt == "abcdefghijk"

    txt = utils.join_text_parts("Le text n'est pas découpé")
    assert txt == "Le text n'est pas découpé"

    txt = utils.join_text_parts("\"Le texte est en\"  \"deux parties\"")
    assert txt == "Le texte est endeux parties"

    dct = utils.get_dkim_dict("a=12; bla=blue; key=base64stuff; last=1")
    assert dct == { "a": "12", "bla": "blue", "key": "base64stuff", "last": "1" }

    infos = utils.get_spf_records("v=spf1 mx all include:coincoin")
    assert len(infos) == 2
    assert infos == [
        {"qualifier": "+", "mechanism": "mx", "modifier": ""},
        {"qualifier": "+", "mechanism": "all", "modifier": ""},
    ]

    infos = utils.get_spf_records("v=spf1 mx include:coincoin ip4:machin/35 exists:any -all")
    assert len(infos) == 5
    assert infos == [
        {"qualifier": "+", "mechanism": "mx", "modifier": ""},
        {"qualifier": "+", "mechanism": "include", "modifier": "coincoin"},
        {"qualifier": "+", "mechanism": "ip4", "modifier": "machin/35"},
        {"qualifier": "+", "mechanism": "exists", "modifier": "any"},
        {"qualifier": "-", "mechanism": "all", "modifier": ""},
    ]

    with pytest.raises(Exception) as e:
        _ = utils.get_spf_records("v=spf1 pabo:plop all -mx")
    assert "Invalid mechanism 'pabo'" in str(e.value)

    with pytest.raises(Exception):
        _ = utils.get_spf_records("not an spf record")

    with pytest.raises(Exception):
        _ = utils.get_spf_records("v=spf1 mx ip4 all")

    with pytest.raises(Exception):
        _ = utils.get_spf_records("v=spf1 mx ip6 all")

    with pytest.raises(Exception):
        _ = utils.get_spf_records("v=spf1 include all")

    with pytest.raises(Exception) as e:
        _ = utils.get_spf_records("v=spf1 all:something")
    assert "Weird 'all'" in str(e.value)

    with pytest.raises(Exception):
        _ = utils.get_spf_records("v=spf1 include.broken -all")

    with pytest.raises(Exception):
        _ = utils.get_spf_records("v=spf1 exists all")

def test_spf():
    with pytest.raises(Exception) as e:
        info = spf.SpfInfo("\"Ceci n'est pas un SPF\"")
    assert "does not look like" in str(e.value)

    with pytest.raises(Exception) as e:
        info = spf.SpfInfo("\"v=spf1 mx ip4:1.2.3.4/32 include:toto.fr\"")
    assert "end with 'all'" in str(e.value)

    info = spf.SpfInfo(
        "\"v=spf1 mx ip4:1.2.3.4/32 include:_spf.toto.fr -include:caca.toto.fr -all\""
    )
    assert isinstance(info, spf.SpfInfo)
    assert info.does_include("_spf.toto.fr")
    assert not info.does_include("pala.toto.fr")
    assert not info.does_include("caca.toto.fr")

    info = spf.SpfInfo(
        "\"v=spf1 mx include:spf.fdn.fr ip4:80.67.169.19 ip6:2001:910:800::19 ~all\""
    )
    assert isinstance(info, spf.SpfInfo)

def test_dkim():
    with pytest.raises(Exception):
        info = dkim.DkimInfo("\"coin=pan; v=DKIM1; h=toto\"")

    info = dkim.DkimInfo("\"v=DKIM1; h=sha256; k=rsa; p=coincoin\"")
    assert isinstance(info, dkim.DkimInfo)
    assert info.elems["v"] == "DKIM1"
    assert info.elems["h"] == "sha256"
    assert info.elems["k"] == "rsa"
    assert info.elems["p"] == "coincoin"

    info2 = dkim.DkimInfo("\"v=DKIM1; h=sha256; k=rsa; p=coin\" \"coin\"")
    assert isinstance(info2, dkim.DkimInfo)
    assert info == info2

    dkim_public = ("mecol._domainkey.mail.numerique.gouv.fr IN TXT (" +
        """"v=DKIM1; h=sha256; k=rsa; "
                "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR"
                "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
                "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
                "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
                "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
                "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
                "LwIDAQAB") ; -- This is a real from production domain
        """)
    info = dkim.DkimInfo(dkim_public)
    assert isinstance(info, dkim.DkimInfo)
    assert info.elems["v"] == "DKIM1"
    assert info.elems["h"] == "sha256"
    assert info.elems["k"] == "rsa"
    assert info.elems["p"] == (
        "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR" +
        "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
        "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
        "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
        "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
        "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
        "LwIDAQAB"
    )

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
    assert len(ck_dom.errs) == 5
    codes = [ err["code"] for err in ck_dom.errs ]
    assert "wrong_mx" in codes
    assert "wrong_cname_webmail" in codes
    assert "wrong_cname_imap" in codes
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
        dkim_selector = "mecol",
        dkim_public = ("mecol._domainkey.mail.numerique.gouv.fr IN TXT (" +
        """"v=DKIM1; h=sha256; k=rsa; "
                "p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2dg8Bt0+p4EEIGF3udBpR"
                "psTd9B0UUzZPTJo64fwijJxFo8RgVUOe8vV6xzhGI22ldMAl6fYNsXih7p/AhEk+CpH"
                "QBFuittufD6Q8XyNrYMblHHfUKlkdy63Bi9v784qc1bWVI+/YRuFzEVnxQkNlbNyKFr"
                "ulZ6J/f7LR1sreSZakMHgy3ePp0QS9oUxs8tYxzWTSfnTS/VAv7"
                "GD4VoZMvLSa+u1fikagc5t3xg76P9twzBOjuFFqIFg+wPGzZZWpzSh/yfcMWHg+eLxk"
                "sxcronXnNZNnfPppNdu2Id28amHB/WB/4vqmgeM3xYIZWETDvZZIjVOzlxGtfgLuNlV"
                "LwIDAQAB") ; -- This is a real from production domain
        """),
        dkim_private = "Coin coin très secret",
    )

    ck_dom = domain.Domain(db_dom)
    ck_dom.check()
    assert ck_dom.valid is True


