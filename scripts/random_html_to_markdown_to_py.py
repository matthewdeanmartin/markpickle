"""
Can we use markpickle as a sort of HTML to Markdown to Python parser?

Seems to work better if
"""
import html2text
import requests

import markpickle


def run() -> None:
    # almost work
    mp = "https://pypi.org/project/markpickle/"

    # don't really work at all

    response = requests.get(mp)
    marks = html2text.html2text(response.text)
    marks = marks.replace("* * *\n", "---\n")
    for item in marks.split("---\n"):
        print("-------------------")
        try:
            result = markpickle.loads(item)
            print(result)
        except TypeError as TE:
            print("!!!!!!!!!!!!!!")
            print(TE)
            print("!!!!!!!!!!!!!!")
        # except NotImplementedError as NIE:
        #     print("!!!!!!!!!!!!!!")
        #     print(NIE)
        #     print("!!!!!!!!!!!!!!")


if __name__ == "__main__":
    run()
