# src/

Source code lives here.

Tests mirror this structure in `tests/` — if `src/parser.py` exists, write `tests/test_parser.py`.

Adjust per project:
- **Python**: package directory with `__init__.py`
- **TypeScript**: `src/` with index entry point
- **C++**: `include/` for headers, `src/` for implementation
- **Rust**: handled by Cargo, this folder may not be needed
