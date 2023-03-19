from mypyc.build import mypycify
from setuptools import setup

setup(
    name="markpickle",
    packages=["markpickle"],
    ext_modules=mypycify(
        [
            "--disallow-untyped-defs",  # Pass a mypy flag
            "markpickle",
        ]
    ),
)
