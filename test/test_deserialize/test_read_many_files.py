import glob

import pytest

import markpickle
from test.utils import locate_file


@pytest.mark.skip("Lots of mixed content errors")
def test_file_from_ts_markdown():
    absolute_file_paths = []

    for file in glob.glob(locate_file("examples_from_ts_markdown", __file__) + "/**/*.md"):
        sample_search_results_file: str = locate_file(file, __file__)
        absolute_file_paths.append(sample_search_results_file)

    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    fail = []
    for file_name in absolute_file_paths:
        with open(file_name, encoding="utf-8") as file:
            try:
                markpickle.loads(
                    file.read(),
                    config=config,
                )
            except Exception as ex:
                fail.append((fail, ex))
    print(fail)
    assert not fail


@pytest.mark.skip("Mixed content errors")
def test_file_from_markdown_to_json():
    absolute_file_paths = []

    for file in glob.glob(locate_file("markdown_to_json_examples", __file__) + "/**/*.md"):
        sample_search_results_file: str = locate_file(file, __file__)
        absolute_file_paths.append(sample_search_results_file)

    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    fail = []
    for file_name in absolute_file_paths:
        with open(file_name, encoding="utf-8") as file:
            try:
                markpickle.loads(
                    file.read(),
                    config=config,
                )
            except Exception as ex:
                fail.append((file_name, ex))
    print(fail)
    assert not fail
