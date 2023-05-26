"""
Machinery for running import foo and getting foo.md to import
"""
import importlib.abc
import os.path
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location


class MdLoader(importlib.abc.Loader):
    def __init__(self, module_path):
        self.module_path = module_path

    def create_module(self, spec):
        return None  # Default behavior, let Python create the module

    def exec_module(self, module):
        with open(self.module_path) as file:
            # TODO: process code blocks here
            code = file.read()
        exec(code, module.__dict__)


class MdImporter(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        module_path = fullname.replace(".", "/") + ".md"
        if not os.path.exists(module_path):
            return None

        spec = spec_from_file_location(fullname, module_path, loader=MdLoader(module_path))
        return spec


# sys.meta_path.append(MdImporter())
