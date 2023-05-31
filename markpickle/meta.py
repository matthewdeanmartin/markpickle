"""
Ad hoc way to add meta data

key1: value1
key2: value2

"""


def extract_keys(value: str) -> dict[str, str]:
    """Extract keys from a Markdown meta section"""
    meta = {}
    for row in value.split("\n"):
        if row.count(":") == 1:
            key, value = row.split(":")
            meta[key] = value
        if not row or row.isspace():
            return meta
    return meta
