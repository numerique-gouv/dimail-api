from .. import oxcli



def test_ox():
    ox_cluster=oxcli.OxCluster()

    oxcli.purge(ox_cluster)

    res = oxcli.list_contexts(ox_cluster)
    res = oxcli.create_context(ox_cluster, 1, "testing", "example.com")
    assert res == oxcli.OxContext(cid=1, name="testing", domains=["example.com"], lmappings="example.com")
