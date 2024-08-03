import re

clean_text = re.compile("^[a-zA-Z0-9/.=_-]+$")

def make_protected_cli(args: list[str]) -> str:
    """Take all the elements for a command line, and protect each of them by
    escaping anything suspicious, and then join them as a command line. So that
    [ "mv", "file one.txt", "file two.csv" ] will create the proper shell command
    line when the filenames are escaped to protect the white space and avoid
    problems."""
    clean = []
    for item in args:
        if clean_text.match(item) is not None:
            clean.append(item)
            continue
        text = "'" + item.replace("'", "\\'") + "'"
        clean.append(text)
    full = " ".join(clean)
    return full


