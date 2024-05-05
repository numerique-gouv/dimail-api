from pydantic import BaseModel
from enum import StrEnum

class Feature(StrEnum):
  Webmail = 'webmail'
  Mailbox = 'mailbox'
  Alias   = 'alias'

class ApiUser(BaseModel):
  name: str
  is_admin: bool
  domains: list['ApiAllowed'] = []
  class ConfigDict:
    from_attribute = True

class ApiDomain(BaseModel):
  name: str
  features: list[Feature]
  mailbox_domain: str | None = None
  webmail_domain: str | None = None
  imap_domains: list[str] | None = None
  smtp_domains: list[str] | None = None
  class ConfigDict:
    from_attribute = True

class ApiAllowed(BaseModel):
  user: str
  domain: str
  class ConfigDict:
    from_attribute = True
  
