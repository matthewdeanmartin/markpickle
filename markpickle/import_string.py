"""
Danger! This executes code. Don't do this unless you control the serialization and deserialization.
"""
import importlib.util
import sys

# def import_code_block(code_block):
#     """TODO"""
#     # check programming language
#     # import if it is code.


def import_code_string(code_string: str, module_name: str) -> None:
    """Import a code string as a module"""
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)

    exec(code_string, module.__dict__)
    sys.modules[module_name] = module


if __name__ == "__main__":

    def test():
        code_string = """
    def greet(name):
        print(f'Hello, {name}!')
        """
        module_name = "my_module"
        import_code_string(code_string, module_name)
        from my_module import greet

        greet("world")
