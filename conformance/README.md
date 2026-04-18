# catdef Conformance Test Suite

This directory contains the official conformance tests for catdef renderers. The suite contains 98 tests organized by subject area.

## Structure

```
conformance/
  fixtures/          catdef files: valid, invalid, and edge-case
  test_parsing.py    catdef file parsing + validation
  test_fields.py     field type rendering (all field types)
  test_search.py     search, sort, filter behavior
  test_themes.py     theme application
  test_levels.py     conformance level feature gates
```

## Running the tests

```bash
pip install pytest
pytest conformance/ -v
```

## Writing a renderer

Your renderer must:

1. Accept a catdef file (`.opencatalog`, `.openthing`, or `.catdef`) or URL to one
2. Parse the catdef JSON according to [CATDEF_SPEC.md](../CATDEF_SPEC.md)
3. Render items in a grid/list with search, sort, and filter
4. Declare its conformance level (L1-L4)
5. Pass all tests for its declared level

## Fixture files

The `fixtures/` directory contains catdef files designed to exercise every corner of the spec:

- `valid_minimal.opencatalog` — smallest possible valid file
- `valid_all_field_types.opencatalog` — one field of every type
- `invalid_no_catdef.catdef` — missing catdef version
- `invalid_bad_field_type.catdef` — unrecognized field type

## Status

The conformance suite is under active development. Contributions welcome.
