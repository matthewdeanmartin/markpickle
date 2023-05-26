from collections import OrderedDict
from pathlib import Path

import markpickle


def run() -> None:
    pathlist = Path("docs/individual").glob("**/*.md")
    for path in pathlist:
        path_in_str = str(path)
        with open(path_in_str) as file:
            value = file.read()
            print(path_in_str)
            try:
                result = markpickle.deserialize_to_nested(value)
            except AttributeError:
                print("Failed!")
                continue
            if isinstance(result, OrderedDict):
                result = dict(result)
            print(result)


if __name__ == "__main__":
    run()
