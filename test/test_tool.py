import pytest
import sys
import io
from pathlib import Path
from typing import List

import markpickle
from markpickle.tool import main as cli_main


def test_stdin_to_stdout(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Test reading from stdin and writing to stdout (default behavior)."""
    markdown_input: str = "- item1\n- item2"
    # This expected object depends on the MarkpickleLibMock.load behavior
    expected_obj: List[str] = ["item1", "item2"]
    expected_string = markpickle.dumps(expected_obj) + "\n"

    monkeypatch.setattr(sys, "stdin", io.StringIO(markdown_input))

    # Call main with no arguments for stdin to stdout
    return_value = cli_main([])

    captured = capsys.readouterr()
    assert captured.out == expected_string  # "- item1\n- item2\n\n"
    assert captured.err == ""
    assert return_value is None  # Successful main() should return None


def test_file_input_to_stdout(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """Test reading from a specified input file and writing to stdout."""
    markdown_content: str = "# My Title\n\nSome content."

    input_file: Path = tmp_path / "input.md"
    input_file.write_text(markdown_content, encoding="utf-8")

    cli_main([str(input_file)])  # Pass input file path as argument

    captured = capsys.readouterr()
    assert captured.out == "# My Title\n\nSome content.\n\n\n"
    assert captured.err == ""


def test_stdin_to_file_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test reading from stdin and writing to a specified output file."""
    markdown_input: str = "- list entry A\n- list entry B"
    expected_obj: List[str] = ["list entry A", "list entry B"]
    expected_string = markpickle.dumps(expected_obj) + "\n"

    monkeypatch.setattr(sys, "stdin", io.StringIO(markdown_input))

    output_file: Path = tmp_path / "output.json"  # Output is JSON-like

    # Use "-" to explicitly denote stdin for infile when outfile is also specified
    cli_main(["-", str(output_file)])

    assert output_file.exists()
    content_written: str = output_file.read_text(encoding="utf-8")
    assert content_written == expected_string  # "- list entry A\n- list entry B\n\n"

    # Ensure nothing is written to stdout when output file is specified
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_file_input_to_file_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test reading from an input file and writing to an output file."""
    markdown_content: str = "# My Title\n\nSome content."

    input_file: Path = tmp_path / "input.md"
    input_file.write_text(markdown_content, encoding="utf-8")

    output_file: Path = tmp_path / "output.json"

    cli_main([str(input_file), str(output_file)])

    assert output_file.exists()
    content_written: str = output_file.read_text(encoding="utf-8")
    assert content_written == "# My Title\n\nSome content.\n\n\n"

    # Ensure nothing is written to stdout when output file is specified
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_empty_input_stdin_to_stdout(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Test empty input from stdin. Mock returns None, output should be 'null'."""
    markdown_input: str = ""
    monkeypatch.setattr(sys, "stdin", io.StringIO(markdown_input))

    cli_main([])

    captured = capsys.readouterr()
    assert captured.out == "\n"
    assert captured.err == ""


def test_tool_docstring_example(capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    """Test the example provided in the tool.py docstring: echo '-a\n-b\n-c' | ..."""
    markdown_input: str = "- a\n- b\n - c"  # Note: no space after hyphen in docstring example

    expected_obj: List[str] = ["a", "b", "c"]
    expected_string = markpickle.dumps(expected_obj) + "\n"

    monkeypatch.setattr(sys, "stdin", io.StringIO(markdown_input))

    cli_main([])

    captured = capsys.readouterr()
    assert captured.out == expected_string  # "-a\n-b\n-c\n"
    assert captured.err == ""
