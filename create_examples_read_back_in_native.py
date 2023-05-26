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
                result = markpickle.loads(value)
            except NotImplementedError:
                print("Failed!")
            print(result)


if __name__ == "__main__":
    run()
