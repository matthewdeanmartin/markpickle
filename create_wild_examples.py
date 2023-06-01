"""Just check if anything blows up, it might not be sensible."""
import glob

import markpickle
from test.utils import locate_file


def run():
    absolute_file_paths = []

    for file in glob.glob(
        locate_file("test/test_deserialize/markdown_to_json_examples", __file__) + "/**/*.md", recursive=True
    ):
        sample_search_results_file: str = locate_file(file, __file__)
        absolute_file_paths.append(sample_search_results_file)
    assert absolute_file_paths
    config = markpickle.Config()
    config.headers_are_dict_keys = True
    config.dict_as_table = False
    config.child_dict_as_table = False
    for file_name in absolute_file_paths:
        with open(file_name, encoding="utf-8") as file:
            some_markdown = file.read()
            result = markpickle.loads(
                some_markdown,
                config=config,
            )
            print(file_name[:-3] + ".py")
            with open(file_name[:-3] + ".py", "w", encoding="utf-8") as output:
                output.write("X = ")
                output.write(str(result))


if __name__ == "__main__":
    run()
