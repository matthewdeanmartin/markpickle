import glob
import json
from test.utils import locate_file

import markpickle


def test_file():
    absolute_file_paths = []
    # relative_file_paths = [
    #     "data/recordation_william_gibson.json",
    #     "data/registration_william_gibson.json",
    #     "data/acquisition_william_gibson.json",
    #     "data/registration_moby_dick_card_catalog.json",
    #     "data/one_hundred_records.json",
    #     "data/another_one_hundred_records.json",
    #     "data/sample.json",
    #     "data/sample2.json",
    #     "data/single_doc.json",
    #     "data/internal1.json",
    #     "data/internal2.json",
    # ]
    for file in glob.glob(locate_file("data", __file__) + "/*.json"):
        sample_search_results_file: str = locate_file(file, __file__)
        absolute_file_paths.append(sample_search_results_file)

    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    for file_name in absolute_file_paths:
        with open(file_name, encoding="utf-8") as file:
            some_dict = json.loads(file.read())
            result = markpickle.dumps(
                some_dict,
                config=config,
            )
            print(result)
