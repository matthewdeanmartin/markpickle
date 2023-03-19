from test.test_serialize.example_types import Animal, Person

import markpickle
from markpickle import dumps


def test_serialize_dataclass():
    person = Person("Alice", 30)
    result = dumps(person)
    assert result == "# name\nAlice\n# age\n30\n"


def test_serialize_class():
    animal = Animal("Dog")
    result = dumps(animal)
    assert result == "# species\nDog\n"


def test_serialize_module():
    result = dumps(markpickle)
    # whoa, that is ugly
    assert "# __name__\nmarkpickle\n" in result
