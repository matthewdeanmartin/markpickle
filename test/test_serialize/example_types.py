from dataclasses import dataclass


@dataclass
class Person:
    name: str
    age: int


class Animal:
    legs = 4

    def __init__(self, species):
        self.species = species
