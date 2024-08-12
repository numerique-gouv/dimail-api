
from .. import dkcli

def test_dkcli(log, dk_manager):
    log.info("Faisons des tests")
    (priv, dns) = dkcli.make_dkim_key("select", "domain.com")
