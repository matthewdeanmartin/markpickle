import glob
import json
from test.utils import locate_file

import markpickle


def test_file():
    absolute_file_paths = []

    for file in glob.glob(locate_file("data", __file__) + "/*.json"):
        sample_search_results_file: str = locate_file(file, __file__)
        absolute_file_paths.append(sample_search_results_file)

    config = markpickle.Config()
    # Only works for shallow nests (2 levels tops)

    config.headers_are_dict_keys = True
    config.serialize_dict_as_table = False
    config.serialize_child_dict_as_table = False
    for file_name in absolute_file_paths:
        with open(file_name, encoding="utf-8") as file:
            some_dict = json.loads(file.read())
            result = markpickle.dumps(
                some_dict,
                config=config,
            )
            with open(file_name.replace(".json", ".md"), "w", encoding="utf-8") as output:
                output.write(result)
