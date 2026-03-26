from pathlib import Path

import markpickle

BOOKS_MARKDOWN_PATH = Path(__file__).resolve().parents[1] / "docs" / "individual" / "books_multi.md"

EXPECTED_BOOKS = [
    [
        {"title": "Pride and Prejudice", "author": "Jane Austen", "published": 1813},
        {"title": "Alice's Adventures in Wonderland", "author": "Lewis Carroll", "published": 1865},
        {"title": "Frankenstein", "author": "Mary Shelley", "published": 1818},
    ],
    ["Pride and Prejudice", "Alice's Adventures in Wonderland", "Frankenstein"],
    {
        "title": "The Adventures of Sherlock Holmes",
        "author": "Arthur Conan Doyle",
        "published": 1892,
        "form": "Short story collection",
        "public_domain": True,
    },
]


def test_books_markdown_loads_to_expected_python_objects() -> None:
    markdown = BOOKS_MARKDOWN_PATH.read_text(encoding="utf-8")

    books = list(markpickle.loads_all(markdown))

    assert books == EXPECTED_BOOKS


def test_books_python_roundtrips_back_to_markdown() -> None:
    markdown = BOOKS_MARKDOWN_PATH.read_text(encoding="utf-8")

    books = list(markpickle.loads_all(markdown))
    rendered = markpickle.dumps_all(books)

    assert list(markpickle.loads_all(rendered)) == EXPECTED_BOOKS
    assert "| title" in rendered
    assert "Pride and Prejudice" in rendered
    assert "Frankenstein" in rendered
    assert "- Alice's Adventures in Wonderland" in rendered
    assert "# title" in rendered
    assert "The Adventures of Sherlock Holmes" in rendered
