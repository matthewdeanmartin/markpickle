import platform

import mistune

print(
    "{} {}; markpickle {}".format(
        platform.python_implementation(),
        platform.python_version(),
        mistune.__version__,
    )
)
