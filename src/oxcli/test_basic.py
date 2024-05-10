from .. import oxcli


def test_ox():
    ox_cluster = oxcli.OxCluster()

    ox_cluster.purge()

    res = ox_cluster.list_contexts()
    res = ox_cluster.create_context(1, "testing", "example.com")
    assert res == oxcli.OxContext(
        cid=1, name="testing", domains=["example.com"], cluster=ox_cluster
    )

    res = ox_cluster.add_mapping(1, "tutu.net")
    assert res == oxcli.OxContext(
        cid=1, name="testing", domains=["example.com", "tutu.net"], cluster=ox_cluster
    )
