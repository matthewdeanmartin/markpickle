from test.test_serialize.example_types import Animal, Person

from markpickle.simplify_types import class_to_dict


def test_dataclass():
    person = Person("Alice", 30)
    expected_dict = {"name": "Alice", "age": 30}
    assert class_to_dict(person) == expected_dict


def test_class():
    animal = Animal("Dog")
    expected_dict = {"species": "Dog"}
    assert class_to_dict(animal) == expected_dict


def test_instance():
    person = Person("Bob", 40)
    person_dict = class_to_dict(person)
    expected_dict = {"name": "Bob", "age": 40}
    assert person_dict == expected_dict
