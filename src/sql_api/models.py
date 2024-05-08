import sqlalchemy as sa
import sqlalchemy.orm as orm

from .database import Api

class DBUser(Api):
    __tablename__ = "users"
    name = sa.Column(sa.String(32), primary_key=True)
    is_admin = sa.Column(sa.Boolean, default=False)
    fullname = sa.Column(sa.String(64), nullable=True)
    domains: orm.Mapped[list["DBDomain"]] = orm.relationship(
        secondary="allowed", back_populates="users"
    )

    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if (
            self.name == other.name
            and self.is_admin == other.is_admin
            and self.fullname == other.fullname
        ):
            return True
        return False


class DBDomain(Api):
    __tablename__ = "domains"
    name = sa.Column(sa.String(200, collation="ascii_bin"), primary_key=True)
    features = sa.Column(sa.JSON(), nullable=False)
    webmail_domain = sa.Column(sa.String(200, collation="ascii_bin"), nullable=True)
    mailbox_domain = sa.Column(sa.String(200, collation="ascii_bin"), nullable=True)
    imap_domains = sa.Column(sa.JSON(), nullable=True)
    smtp_domains = sa.Column(sa.JSON(), nullable=True)
    users: orm.Mapped[list["DBUser"]] = orm.relationship(
        secondary="allowed", back_populates="domains"
    )


class DBAllowed(Api):
    __tablename__ = "allowed"
    user = sa.Column(sa.String(32), sa.ForeignKey("users.name"), primary_key=True)
    domain = sa.Column(
        sa.String(200, collation="ascii_bin"), sa.ForeignKey("domains.name"), primary_key=True
    )

    def __repr__(self):
        return 'sql_api.DBAllowed("%s","%s")' % (self.user, self.domain)
