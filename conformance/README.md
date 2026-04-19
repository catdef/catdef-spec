# catdef Conformance Test Suite

This directory contains the official conformance tests for catdef renderers. The suite contains 98 tests organized by subject area.

## Structure

```
conformance/
  fixtures/          catdef files: valid, invalid, and edge-case
  policies/          policy-compliance tests (value #9; first-class dimension at v1.4+)
  test_parsing.py    catdef file parsing + validation
  test_fields.py     field type rendering (all field types)
  test_search.py     search, sort, filter behavior
  test_themes.py     theme application
  test_levels.py     conformance level feature gates
```

## Test dimensions

The suite tests catdef conformance across three first-class dimensions, each weighted equally:

- **Structure and content** — field types, subcats, views, templates, value shapes. Verified by `test_parsing.py`, `test_fields.py`, and the value-shape coverage extensions from CA-006.
- **Forward compatibility** — value #5. A reader MUST gracefully ignore unknown fields; a writer MUST stamp per the Feature-Version Index. Verified by `test_parsing.py` forward-compat fixtures and the `ft-version-*` tests from CA-002.
- **Policy compliance** — value #9. An author-declared policy (`.machine-translate: "Never"` and future closed-vocabulary policies) is a constraint on conformant implementations. Verified by `policies/` — see [policies/README.md](policies/README.md).

A runtime that passes structure and forward-compat tests but fails a policy-compliance test is not conformant at its declared level.

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
