import markpickle.gui.randgen as randgen


def test_rand_word_and_words_are_built_from_random_choices(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 4)
    monkeypatch.setattr(randgen.random, "choices", lambda _letters, k: list("test"))

    assert randgen._rand_word() == "test"
    assert randgen._rand_words(2) == "test test"
    assert randgen._rand_identifier() == "Test"


def test_low_level_random_helpers_and_scalar_block(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 7)
    monkeypatch.setattr(randgen.random, "uniform", lambda _a, _b: 3.14159)
    monkeypatch.setattr(randgen.random, "choice", lambda _items: True)
    monkeypatch.setattr(randgen, "_rand_scalar_str", lambda: "value")

    assert randgen._rand_int() == 7
    assert randgen._rand_float() == 3.14
    assert randgen._rand_bool() is True
    assert randgen._scalar_block() == "value\n"


def test_rand_scalar_string_covers_each_supported_kind(monkeypatch) -> None:
    monkeypatch.setattr(randgen, "_rand_words", lambda _n=3: "hello world")
    monkeypatch.setattr(randgen, "_rand_int", lambda: 42)
    monkeypatch.setattr(randgen, "_rand_float", lambda: 1.25)

    values = iter(["word", "int", "float", "bool", "False", "none"])
    monkeypatch.setattr(randgen.random, "choice", lambda _items: next(values))
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 2)

    assert randgen._rand_scalar_str() == "hello world"
    assert randgen._rand_scalar_str() == "42"
    assert randgen._rand_scalar_str() == "1.25"
    assert randgen._rand_scalar_str() == "False"
    assert randgen._rand_scalar_str() == "None"


def test_unordered_list_block_can_emit_nested_lists(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 2)
    monkeypatch.setattr(randgen, "_rand_word", lambda: "branch")
    monkeypatch.setattr(randgen, "_rand_scalar_str", lambda: "leaf")

    random_values = iter([0.1, 0.9, 0.9, 0.9])
    monkeypatch.setattr(randgen.random, "random", lambda: next(random_values))

    result = randgen._unordered_list_block()

    assert result == "- branch\n    - leaf\n    - leaf\n- leaf\n"


def test_ordered_list_code_block_table_and_definition_list(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 2)
    scalar_values = iter(["one", "two"])
    monkeypatch.setattr(randgen, "_rand_scalar_str", lambda: next(scalar_values))
    assert randgen._ordered_list_block() == "1. one\n2. two\n"

    choice_values = iter(["python"])
    monkeypatch.setattr(randgen.random, "choice", lambda _items: next(choice_values))
    monkeypatch.setattr(randgen.random, "random", lambda: 0.5)
    monkeypatch.setattr(randgen, "_rand_word", lambda: "value")
    monkeypatch.setattr(randgen, "_rand_int", lambda: 7)
    assert randgen._code_block() == "```python\nvalue = 7\nvalue = 7\n```\n"

    monkeypatch.setattr(randgen, "_rand_identifier", lambda: "Col")
    monkeypatch.setattr(randgen, "_rand_int", lambda: 9)
    assert randgen._table_block() == "| Col | Col |\n| --- | --- |\n| 9 | 9 |\n| 9 | 9 |\n"

    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 2)
    monkeypatch.setattr(randgen, "_rand_identifier", lambda: "Term")
    monkeypatch.setattr(randgen, "_rand_words", lambda _n=3: "two words")
    assert randgen._def_list_block() == "Term\n:   two words\n\nTerm\n:   two words\n"


def test_dict_block_and_random_markdown_dispatch(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 2)

    identifiers = iter(["Root", "Child", "Leaf", "Other"])
    monkeypatch.setattr(randgen, "_rand_identifier", lambda: next(identifiers))
    monkeypatch.setattr(randgen, "_scalar_block", lambda: "scalar\n")
    monkeypatch.setattr(randgen, "_unordered_list_block", lambda depth=0: "- item\n")
    monkeypatch.setattr(randgen, "_ordered_list_block", lambda: "1. item\n")

    random_values = iter([0.1, 0.9, 0.9, 0.9])
    monkeypatch.setattr(randgen.random, "random", lambda: next(random_values))
    monkeypatch.setattr(randgen.random, "choice", lambda _items: "scalar")

    result = randgen._dict_block()

    assert result.startswith("# Root\n")
    assert "## Child\n\nscalar\n" in result
    assert "## Leaf\n\nscalar\n" in result
    assert "# Other\n\nscalar\n" in result

    monkeypatch.setattr(randgen, "_SCENARIOS", [("demo", lambda: "body\n")])
    monkeypatch.setattr(randgen.random, "choice", lambda items: items[0])

    assert randgen.random_markdown() == ("demo", "body\n")


def test_dict_block_can_emit_list_and_ordered_children(monkeypatch) -> None:
    monkeypatch.setattr(randgen.random, "randint", lambda _a, _b: 1)
    monkeypatch.setattr(randgen, "_rand_identifier", lambda: "Root")
    monkeypatch.setattr(randgen.random, "random", lambda: 0.9)
    monkeypatch.setattr(randgen, "_unordered_list_block", lambda depth=0: "- item\n")
    monkeypatch.setattr(randgen, "_ordered_list_block", lambda: "1. item\n")

    monkeypatch.setattr(randgen.random, "choice", lambda _items: "list")
    assert randgen._dict_block() == "# Root\n\n- item\n\n"

    monkeypatch.setattr(randgen.random, "choice", lambda _items: "ordered")
    assert randgen._dict_block() == "# Root\n\n1. item\n\n"
