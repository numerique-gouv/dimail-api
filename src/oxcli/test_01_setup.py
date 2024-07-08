import pytest

from .. import oxcli


def test_setup():
    oxcli.begin_test_clusters()

    with pytest.raises(Exception) as e:
        oxcli.get_cluster_info("essai")
    assert "The cluster essai does not exist" in str(e.value)

    with pytest.raises(Exception) as e:
        oxcli.set_default_cluster("essai")
    assert "Cluster essai does not exist" in str(e.value)

    oxcli.declare_cluster("essai", "url")
    with pytest.raises(Exception) as e:
        oxcli.declare_cluster("essai", "autre_url")
    assert "Cluster essai already declared" in str(e.value)

    with pytest.raises(Exception) as e:
        name, url, args = oxcli.get_cluster_info()
        print(f"J'ai trouve le cluster {name} sur l'url {url}")
    assert "no default" in str(e.value)

    name, url, args = oxcli.get_cluster_info("essai")
    assert name == "essai"
    assert url == "url"

    oxcli.set_default_cluster("essai")
    name, url, args = oxcli.get_cluster_info()
    assert name == "essai"
    assert url == "url"

    oxcli.end_test_clusters()



