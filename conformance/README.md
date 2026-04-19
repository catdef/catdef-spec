# catdef Conformance Test Suite

This directory contains the official conformance tests for catdef renderers. The suite contains 164 tests organized by subject area, plus 1 `xfail` tracking a known canonical drift (see §"The ft-shape-07 canonical regression" below).

## Structure

```
conformance/
  fixtures/                  catdef files: valid, invalid, and edge-case (25 files as of v1.4)
  policies/                  policy-compliance tests (value #9; first-class dimension at v1.4+)
    test_i18n_policies.py      ft-i18n-07/08/09 — .context preservation, .machine-translate enforcement
  test_parsing.py            catdef parsing + validation, forward-compat
  test_field_values.py       field-type value shapes incl. CA-006 Date circa/range, Money range,
                             Number range, URL object + polymorphic translatable fields + ft-shape-01..07
  test_photo_transforms.py   photo crop / rotate / deskew
  test_versioning.py         CA-002 writer-strict stamping + Feature-Version Index + ft-version-01..04
  test_subcat_values.py      CA-003 subcats-authoritative + ft-subcat-values-01..05
  test_catio_bundle.py       CA-001 ZIP outer-archive extension + ft-catio-01..05
  test_i18n.py               polymorphic-field fallback (RFC 4647 Lookup) + ft-i18n-01..06
```

## The ft-shape-07 canonical regression

**ft-shape-07** is a load-bearing regression test: it runs the extended value-shape validator against `canonical/catalog.opencatalog` and expects zero errors. If either the canonical or the validator drifts, the test fails, making validator-vs-canonical drift structurally detectable rather than discoverable only by manual review.

The test currently ships with an `xfail` marker covering one known canonical drift:

> Canonical Artifact template `Date Made` field uses range-shape values on items[1] and items[4] but field_def declares `circa: true` and not `range: true`. Per CA-006 writer-strict validation, that is a canonical-side bug.

The fix is canonical-builder's call — either add `range: true` to the field_def (allowing circa and range values on the same field) or rewrite those items' values to circa-shape.

**If `ft-shape-07` unexpectedly passes** (pytest reports `XPASS`), it means canonical-builder has fixed the drift. The `@pytest.mark.xfail` marker MUST be removed in the same PR that lands the canonical fix, so the test resumes its regular regression-guarding behavior. The xfail is a temporary signpost, not a permanent exemption.

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

The `fixtures/` directory contains catdef files designed to exercise every corner of the spec. Representative fixtures (one per category):

**Parsing / structure**
- `valid_minimal.opencatalog` — smallest possible valid file
- `valid_all_field_types.opencatalog` — one field of every type
- `invalid_no_catdef.catdef` — missing catdef version
- `invalid_bad_field_type.catdef` — unrecognized field type

**Photo transforms**
- `valid_photo_transforms.opencatalog`, plus `invalid_*` fixtures for rotation, crop bounds, deskew corners

**Value shapes (CA-006, v1.4)**
- `valid_v13_value_shapes.opencatalog` — Date circa/range, Money range, Number range, URL object

**Version stamping (CA-002)**
- `valid_stamp_matches_features.opencatalog`, `valid_stamp_newer_than_features.opencatalog`, `invalid_stamp_older_than_features.opencatalog`

**Subcat value resolution (CA-003)**
- `valid_subcat_values_only.opencatalog`, `valid_subcat_plus_matching_data_values.opencatalog`, `valid_data_values_only.opencatalog`, `valid_empty_subcat_plus_data_values.opencatalog`, `invalid_data_values_superset.opencatalog`

**CATIO bundles (CA-001)**
- `valid_raw_opencatalog.opencatalog` (ZIP fixtures are built at test time)

**i18n (polymorphic translatable fields + policies)**
- `bilingual_labels.opencatalog`, `monolingual_french.opencatalog`, `polymorphic_no_primary.opencatalog`, `locale_variants_fr_ca.opencatalog`, `mt_never_content.opencatalog`

## Status

The conformance suite covers all five v1.4 release proposals (CA-001/002/003/006 + i18n). Contributions welcome; additions land as part of their respective spec proposals per CLAUDE.md.
