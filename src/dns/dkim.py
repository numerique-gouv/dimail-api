from . import utils

class DkimInfo:
    elems: dict
    def __init__(self, text: str):
        (_, text) = utils.get_txt_from_dns_record(text)
        text = utils.join_text_parts(text)
        if not text.startswith("v=DKIM1;"):
            raise Exception("This does not look like a Dkim TXT record")
        self.elems = utils.get_dkim_dict(text)
        if "v" not in self.elems:
            raise Exception("Missing v part (version)")
        if "h" not in self.elems:
            raise Exception("Missing h part (hash algo)")
        if "k" not in self.elems:
            raise Exception("Missing k part (key type)")
        if "p" not in self.elems:
            raise Exception("Missing p part (public key)")

    def __eq__(self, other) -> bool:
        if not isinstance(other, DkimInfo):
            return False
        if self.elems == other.elems:
            return True
        return False

    def __str__(self) -> str:
        return f"DkimInfo(v={self.v}, h={self.h}, k={self.k}, p={self.p})"


