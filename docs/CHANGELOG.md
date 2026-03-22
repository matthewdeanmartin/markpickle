# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-03-21

### Breaking Changes

- `infer_scalar_types=False` now truly returns strings for everything (previously, bool, None, and date inference bypassed this flag)
- `none_values` config list is now consulted during deserialization (previously ignored; only `none_string` was checked)
- Ordered lists (`1. item`) now deserialize as tuples by default (new config: `ordered_list_as_tuple=True`)
- Non-flat child dicts (containing nested dicts/lists) now serialize as ATX headers instead of tables, even when `serialize_child_dict_as_table=True`
- `serialize_child_dict_as_table=False` now recurses with deeper ATX headers (`## key`) instead of bullet-style `- key : value`

### Fixed

- **dump_all stream bug**: `dump_all()` stream version now correctly emits `---` separators between documents (counter variable was never incremented)
- **datetime loses time**: `datetime.datetime` now serializes with time component using `serialized_datetime_format` (previously `isinstance(value, datetime.date)` matched before `datetime.datetime` check)
- **Negative ints become float**: Negative integers like `-5` now correctly deserialize as `int` (previously `isnumeric()` returned False for negative numbers, falling through to `float()`)
- **3-level ATX nesting crash**: Documents with 3+ levels of ATX headers (`# a / ## b / ### c`) now deserialize correctly as nested dicts instead of raising `TypeError("Unconsumed header...")`
- **Table heuristic too aggressive**: Child dicts containing nested dicts/lists now use ATX header recursion instead of being forced into flat tables

### Added

- **Tuples as ordered lists**: Tuples serialize as markdown ordered lists (`1. item`) and ordered lists deserialize as tuples. Config: `serialize_tuples_as_ordered_lists`, `ordered_list_as_tuple`
- **Unicode text formatting**: New `unicode_text` module converts markdown bold/italic/code to Unicode Mathematical Alphanumeric Symbols for round-trip preservation. Functions: `to_bold()`, `to_italic()`, `to_monospace()`, `from_bold()`, `from_italic()`, `from_monospace()`, `markdown_inline_to_unicode()`, `unicode_to_markdown()`. Config: `preserve_formatting_as_unicode`
- **YAML front matter support**: New `loads_with_frontmatter()` and `dumps_with_frontmatter()` functions for reading/writing YAML front matter metadata. Config: `parse_yaml_frontmatter`
- **Complex number serialization**: Serialize/deserialize Python `complex` type (e.g., `3+4j`). Config: `infer_complex_types`
- **Decimal serialization**: Serialize/deserialize `decimal.Decimal` instead of float. Config: `infer_decimal_types`
- **UUID serialization**: Serialize/deserialize `uuid.UUID` with pattern detection. Config: `infer_uuid_types`
- `is_flat_dict()` helper for table heuristic decisions

## [1.6.4] - 2026-03-08

### Fixed

- Fixed broken wheel

## [1.6.3] - 2026-03-08

### Removed

- This version was yanked from PyPI

### Added

- Add support for more complex table headers
- Support for documents with just headers

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

## [1.6.1] - 2023-06-08

### Added

- Python 3.9 support

## [1.6.0] - 2023-06-08

### Changed

- Initial release of the 1.6.x series

## [1.5.1] - 2023-06-08

### Fixed

- Fix mypy typing
- Pin mistune to <3.0.0

### Changed

- Better table support
- Less ambitious image type handling

## [1.5.0] - 2023-05-30

### Changed

- Tables less buggy

## [1.4.0] - 2023-05-30

### Added

- ATX headers as dictionary support

## [1.3.0] - 2023-05-26

### Added

- Improved CLI
- More examples

## [1.2.0] - 2023-05-13

### Added

- Support for binary data, serialized as images with data URLs

## [1.1.0] - 2023-03-19

### Added

- Basic functionality improvements

## [1.0.0] - 2023-03-19

### Added

- Basic functionality
- Markdown to Python data serialization
- Python to Markdown deserialization
- CLI support
