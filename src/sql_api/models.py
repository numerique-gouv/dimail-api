from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped, relationship

from .database import Api

#allowed = Table(
#  'allowed',
#  Base.metadata,
#  Column("user", String(32), ForeignKey("users.name"), primary_key=True),
#  Column("domain", String(200), ForeignKey("domains.name"), primary_key=True)
#)

class ApiUser(Api):
    __tablename__='users'
    name = Column(String(32), primary_key=True)
    is_admin = Column(Boolean, default=False)
    fullname = Column(String(64), nullable=True)
    # domains = relationship("ApiAllowed")
    domains: Mapped[list['ApiDomain']] = relationship(secondary="allowed", back_populates="users")
    def __eq__(self, other):
        if not isinstance(self, other.__class__):
            return False
        if self.name == other.name and self.is_admin == other.is_admin and self.fullname == other.fullname:
            return True
        return False


class ApiDomain(Api):
  __tablename__='domains'
  name = Column(String(200, collation='ascii_bin'), primary_key=True)
  features = Column(JSON(), nullable=False)
  webmail_domain = Column(String(200, collation='ascii_bin'), nullable=True)
  mailbox_domain = Column(String(200, collation='ascii_bin'), nullable=True)
  imap_domains = Column(JSON(), nullable=True)
  smtp_domains = Column(JSON(), nullable=True)
  users: Mapped[list['ApiUser']] = relationship(secondary="allowed", back_populates="domains")

class ApiAllowed(Api):
  __tablename__='allowed'
  user = Column(String(32), ForeignKey("users.name"), primary_key=True)
  domain = Column(String(200, collation='ascii_bin'), ForeignKey("domains.name"), primary_key=True)
  def __repr__(self):
    return 'ApiAllowed("%s","%s")' % (self.user, self.domain)

