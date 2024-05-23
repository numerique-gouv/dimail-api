import sqlalchemy as sa


def test_mysql_version(mysql_container, log):
    engine = sa.create_engine(mysql_container.get_connection_url())
    with engine.begin() as connection:
        result = connection.execute(sa.text("select version()"))
        version, = result.fetchone()
    assert version.startswith("5.7.17")
