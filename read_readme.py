"""
What happens if you deserialize a typical readme? It won't be a faitful DOM
"""
import pprint

import markpickle

with open("README.md", encoding="utf-8") as file:
    for document in markpickle.load_all(file):
        pprint.pprint(document)
