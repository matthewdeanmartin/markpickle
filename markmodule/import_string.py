"""
Danger! This executes code. Don't do this unless you control the serialization and deserialization.
"""
import importlib.util
import sys

import mistune


def import_md(name: str):
    with open(f"{name}.md") as f:
        string_value = f.read()
        parser = mistune.create_markdown(renderer="ast")
        result = parser.parse(string_value)
        code_string = ""
        for token in result:
            if token["type"] == "block_code" and token["info"] == "python":
                code_string += token["text"]
        print(code_string)
        import_code_string(code_string, name)


def import_code_string(code_string: str, module_name: str) -> None:
    """Import a code string as a module using function. See md_module_support to import using `import` syntax."""
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)

    exec(code_string, module.__dict__)
    sys.modules[module_name] = module


if __name__ == "__main__":
    import_md("hello_module")
    import hello_module

    print(hello_module.some_function("yo!"))

    def something():
        code_string = """
    def greet(name):
        print(f'Hello, {name}!')
        """
        module_name = "my_module"
        import_code_string(code_string, module_name)
        from my_module import greet

        greet("world")
