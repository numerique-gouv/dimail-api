from .. import oxcli


def test_ox(ox_cluster):

    res = ox_cluster.list_contexts()
    assert res == []
    ctx = ox_cluster.create_context(1, "testing", "example.com")
    assert ctx == oxcli.OxContext(
        cid=1, name="testing", domains=["example.com"], cluster=ox_cluster
    )

    # Domain can be added via the cluster...
    ctx = ox_cluster.add_mapping(1, "toto.com")
    assert ctx == oxcli.OxContext(
        cid=1, name="testing", domains=["example.com", "toto.com"], cluster=ox_cluster
    )

    # or via the context
    ctx = ctx.add_mapping("tutu.net")
    assert ctx == oxcli.OxContext(
        cid=1,
        name="testing",
        domains=["example.com", "toto.com", "tutu.net"],
        cluster=ox_cluster,
    )

    ctx = ox_cluster.get_context(1)
    assert isinstance(ctx, oxcli.OxContext)
    assert ctx.cid == 1

    ctx = ox_cluster.get_context(2)
    assert ctx is None

    ctx = ox_cluster.get_context_by_name("testing")
    assert isinstance(ctx, oxcli.OxContext)
    assert ctx.cid == 1

    ctx = ox_cluster.get_context_by_name("doest_not_exist")
    assert ctx is None

    ctx = ox_cluster.get_context_by_domain("example.com")
    assert isinstance(ctx, oxcli.OxContext)
    assert ctx.cid == 1

    ctx = ox_cluster.get_context_by_domain("not-a-real-domain.biz")
    assert ctx is None

    # At the beginning, we have the admin user
    ctx = ox_cluster.get_context(1)
    admin_user = oxcli.OxUser(
        uid=2,
        username="admin_user",
        givenName="Admin",
        surName="Context",
        displayName="Context Admin",
        email="oxadmin@example.com",
        ctx=ctx,
    )

    res = ctx.list_users()
    assert res == [admin_user]

    # User can be created via the context...
    want_user = oxcli.OxUser(
        uid=3,
        username="toto",
        givenName="Given",
        surName="Sur",
        displayName="Given Sur",
        email="toto@tutu.net",
        ctx=ctx,
    )
    got_user = ctx.create_user(
        givenName="Given",
        surName="Sur",
        username="toto",
        domain="tutu.net",
    )
    assert got_user == want_user

    # and not yet from the cluster
    # user = ox_cluster.create_user(...)
    # return ox_cluster.get_context_by_domain(domain).create_user(...)

    res = ctx.list_users()
    assert len(res) == 2

    got_user = ctx.search_user("toto")
    assert got_user == [want_user]

    got_user = ctx.search_user("titi")
    assert got_user == []

    got_user = ctx.get_user_by_email("toto@tutu.net")
    assert got_user == want_user

    got_user = ctx.get_user_by_email("titi@tutu.net")
    assert got_user is None

    got_user = ctx.get_user_by_name("toto")
    assert got_user == want_user

    got_user = ctx.get_user_by_name("titi")
    assert got_user is None


