# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-26

### Added

- Tuples serialize as markdown ordered lists and ordered lists deserialize as tuples. Config: `serialize_tuples_as_ordered_lists`, `ordered_list_as_tuple`
- Unicode text formatting module converts markdown bold/italic/code to Unicode Mathematical Alphanumeric Symbols for round-trip preservation. Functions: `to_bold()`, `to_italic()`, `to_monospace()`, `from_bold()`, `from_italic()`, `from_monospace()`, `markdown_inline_to_unicode()`, `unicode_to_markdown()`. Config: `preserve_formatting_as_unicode`
- YAML front matter support via new `loads_with_frontmatter()` and `dumps_with_frontmatter()` functions. Config: `parse_yaml_frontmatter`
- Complex number serialization and deserialization for the Python `complex` type (e.g., `3+4j`). Config: `infer_complex_types`
- Decimal serialization and deserialization using `decimal.Decimal` instead of float. Config: `infer_decimal_types`
- UUID serialization and deserialization with pattern detection. Config: `infer_uuid_types`
- `is_flat_dict()` helper for table heuristic decisions

### Changed

- `infer_scalar_types=False` now returns strings for everything, bypassing bool/None/date inference (previously those checks ignored this flag)
- `none_values` config list is now consulted during deserialization (previously only `none_string` was checked)
- Ordered lists now deserialize as tuples by default. Config: `ordered_list_as_tuple=True`
- Non-flat child dicts containing nested dicts or lists now serialize as ATX headers instead of tables, even when `serialize_child_dict_as_table=True`
- `serialize_child_dict_as_table=False` now recurses with deeper ATX headers (`## key`) instead of bullet-style `- key : value`

### Fixed

- `dump_all()` stream version now correctly emits `---` separators between documents (counter variable was never incremented)
- `datetime.datetime` now serializes with time component using `serialized_datetime_format` (previously `isinstance(value, datetime.date)` matched before the `datetime.datetime` check)
- Negative integers like `-5` now correctly deserialize as `int` (previously `isnumeric()` returned False for negative numbers, causing fallthrough to `float()`)
- Documents with 3+ levels of ATX headers now deserialize correctly as nested dicts instead of raising `TypeError("Unconsumed header...")`
- Child dicts containing nested dicts or lists now use ATX header recursion instead of being forced into flat table serialization

## [1.6.4] - 2026-03-08

### Added

- Support for more complex table headers
- Support for documents with just headers

### Fixed

- Fixed broken wheel
- Fixed package vulnerabilities

## [1.6.3] - 2026-03-02

### Removed

- This version was yanked from PyPI

### Added

- Support for more complex table headers

### Changed

- Updated pre-commit hooks

### Fixed

- Fixed various package vulnerabilities

## [1.6.2] - 2023-06-17

### Added

- Python 3.14 support

### Changed

- Switched to uv for package management
- Improved GitHub Actions workflows
- Improved build system

## [1.6.1] - 2023-06-09

### Added

- Python 3.9 support

## [1.6.0] - 2023-06-09

### Changed

- Add stress-test examples covering diverse markdown structures to exercise the deserializer
- Add `serialize_child_dict_as_table` config flag to control child dict serialization path

## [1.5.1] - 2023-06-08

### Changed

- Better table support
- Less ambitious image type handling

### Fixed

- Fix mypy typing
- Pin mistune to <3.0.0

## [1.5.0] - 2023-06-01

### Changed

- Improve internal build and CI configuration
- Tables less buggy

## [1.4.0] - 2023-05-31

### Added

- Better table support
- ATX headers as dictionary support

## [1.3.0] - 2023-05-26

### Added

- Add GitHub Actions CI workflow
- Add example scripts with round-trip verification reporting
- Add CLI and devcontainer configuration

## [1.2.0] - 2023-05-13

### Added

- Support for binary data serialized as images with data URLs
- Code blocks importable as modules

## [1.1.0] - 2023-03-19

### Added

- Add `dumps_all` / `loads_all` functions mirroring the json module interface
- Add `split_file` utility for extracting code blocks from markdown
- Add `list_bullet_style` config option to control bullet style in serialized output
- Add docstrings to all `Config` fields

## [1.0.0] - 2023-03-19

### Added

- Basic markdown to Python data serialization
- Python to markdown deserialization
- CLI support
- Functions similar to json dumps/loads

## [0.2.0] - 2023-03-18

### Added

- Initial release

[2.0.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.6.4...v2.0.0
[1.6.4]: https://github.com/matthewdeanmartin/markpickle/compare/v1.6.3...v1.6.4
[1.6.3]: https://github.com/matthewdeanmartin/markpickle/compare/v1.6.2...v1.6.3
[1.6.2]: https://github.com/matthewdeanmartin/markpickle/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/matthewdeanmartin/markpickle/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.5.1...v1.6.0
[1.5.1]: https://github.com/matthewdeanmartin/markpickle/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.4.0...v1.5.0
[1.4.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/matthewdeanmartin/markpickle/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/matthewdeanmartin/markpickle/compare/v0.2.0...v1.0.0
[0.2.0]: https://github.com/matthewdeanmartin/markpickle/releases/tag/v0.2.0
