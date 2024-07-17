
class DkimInfo:
    v: str | None
    h: str | None
    k: str | None
    p: str | None

    def __init__(self, text: str):
        if text.startswith('"'):
            text = text.replace(" ","")
            text = text.replace('"', "")
            text = text.replace("\n", "")
            text = text.replace("\t", "")
        items = text.split(";")
        for item in items:
            print(f"Je regarde l'item {item}")
            (key, val) = item.split("=", 1)
            print(f"key = '{key}' et val = '{val}'")
            setattr(self, key, val)
        if self.v is None or self.h is None or self.k is None or self.p is None:
            raise Exception("Invalid DKIM")

    def __eq__(self, other) -> bool:
        if not isinstance(other, DkimInfo):
            return False
        if self.v == other.v and self.h == other.h and self.k == other.k and self.p == other.p:
            return True
        return False

    def __str__(self) -> str:
        return f"DkimInfo(v={self.v}, h={self.h}, k={self.k}, p={self.p})"


