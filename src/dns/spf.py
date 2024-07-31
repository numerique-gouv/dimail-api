import re

from . import utils

class SpfInfo:
    version: str
    records: list[dict]

    def __init__(self, text: str):
        (_, text) = utils.get_txt_from_dns_record(text)
        text = utils.join_text_parts(text)
        if not text.startswith("v=spf1 "):
            raise Exception("This does not look like a SPF TXT record")
        self.version = "spf1"
        self.records = utils.get_spf_records(text)
        n = len(self.records)-1
        if self.records[n]["mechanism"] != "all":
            raise Exception("An SPF record should end with 'all' mechanism")

    def does_include(self, name: str) -> bool:
        for record in self.records:
            if ( record["mechanism"] == "include" and
                 record["qualifier"] == "+" and
                 record["modifier"] == name ):
                return True
        return False
