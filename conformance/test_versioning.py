"""
catdef Conformance: version-stamping tests (CA-002).

Per CATDEF_SPEC.md §Versioning §Writer obligation on version stamping:

- A writer MUST stamp the minimum version that defines every feature used.
- A writer MUST NOT emit a stamp that post-dates any feature (over-stamping
  permitted but discouraged).
- A reader MUST NOT reject a mis-stamped document; MAY warn.

The writer-strict / reader-lenient asymmetry is the same Postel's Law
pattern used elsewhere in v1.4 (CA-003 superset validation,
polymorphic-field unknown keys).

Tests here cover the writer side. Reader-side graceful-ignore is
covered in test_parsing.py (forward-compat fixtures).

This module implements a pragmatic required_minimum_version() helper
covering the most-distinctive features per version (types introduced,
top-level fields, field_def attributes). A comprehensive validator
would expand coverage; this is sufficient for ft-version-01..04.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


# Feature-version index, condensed to what the tests here need. Authoritative
# definition lives in CATDEF_SPEC.md §Versioning §Feature-Version Index.

V1_0_TYPES = {"String", "Integer", "RichText", "Enumerated", "Photo"}
V1_1_TYPES = {"Number", "GeoLocation", "Date", "Money", "Boolean", "CloudFile", "URL", "Table"}
# v1.2 added subcats; v1.3 added inherits_from/views/embed/scorable/range/
# extended product + subcat Photo/Enumerated fields; v1.4 added
# primaryLocale/polymorphic/Policy Registry/URL object schema.

V1_3_PRODUCT_EXT_KEYS = {"phone", "website", "address", "hours", "social", "sections"}


def _vtuple(v: str) -> tuple[int, ...]:
    """Parse a semver-ish string ('1.3', '1.4', '1.3.1') into a comparable tuple."""
    return tuple(int(p) for p in v.split(".") if p.isdigit())


def _max_version(a: str, b: str) -> str:
    """Return the larger of two semver-ish strings."""
    return a if _vtuple(a) >= _vtuple(b) else b


def required_minimum_version(data: dict) -> str:
    """Walk a catdef and return the minimum version that defines every feature used.

    Returns a semver-ish string ('1.0', '1.1', '1.2', '1.3', '1.4').
    """
    required = "1.0"

    # Top-level feature probes.
    if "subcats" in data:
        required = _max_version(required, "1.2")
        # Subcat Photo/Enumerated field_defs are v1.3 enrichments.
        for sc in data.get("subcats", {}).values():
            for fd in sc.get("field_defs", []) if isinstance(sc, dict) else []:
                if fd.get("type") in ("Photo", "Enumerated"):
                    required = _max_version(required, "1.3")
    if "inherits_from" in data:
        required = _max_version(required, "1.3")
    if "views" in data:
        required = _max_version(required, "1.3")
    if "embed" in data:
        required = _max_version(required, "1.3")
    if "primaryLocale" in data:
        required = _max_version(required, "1.4")

    # Extended product fields → 1.3.
    product = data.get("product", {})
    if isinstance(product, dict):
        if set(product.keys()) & V1_3_PRODUCT_EXT_KEYS:
            required = _max_version(required, "1.3")

    # Template / field_def / item-value probes.
    for tmpl in data.get("templates", []):
        for fd in tmpl.get("field_defs", []):
            ft = fd.get("type")
            if ft in V1_1_TYPES:
                required = _max_version(required, "1.1")
            if fd.get("range") is True:
                required = _max_version(required, "1.3")
            if fd.get("scorable"):
                required = _max_version(required, "1.3")

    # Item-level probes: polymorphic translatable-field objects, URL objects.
    for item in data.get("data", {}).get("items", []):
        for v in (item.get("fields") or {}).values():
            if isinstance(v, dict):
                if v and all(isinstance(k, str) and k.startswith(".") for k in v):
                    required = _max_version(required, "1.4")
                if "url" in v and isinstance(v.get("url"), str):
                    required = _max_version(required, "1.4")

    return required


def stamp_conforms(data: dict) -> bool:
    """Writer-side check: does the declared catdef stamp cover every feature used?"""
    declared = data.get("catdef", "1.0")
    required = required_minimum_version(data)
    return _vtuple(declared) >= _vtuple(required)


class TestFeatureVersionIndex:
    """Spot-checks the feature-version helper against fixtures."""

    def test_minimal_is_v1_0(self):
        data = _load("valid_minimal.opencatalog")
        # Uses only v1.0 types; no subcats/views/etc.
        assert required_minimum_version(data) == "1.0"

    def test_all_field_types_is_v1_1_or_later(self):
        data = _load("valid_all_field_types.opencatalog")
        # Uses v1.1 types (Number, Money, ...).
        assert _vtuple(required_minimum_version(data)) >= _vtuple("1.1")

    def test_value_shapes_v14_fixture_requires_v1_4(self):
        data = _load("valid_v13_value_shapes.opencatalog")
        # Has a URL object → v1.4.
        assert required_minimum_version(data) == "1.4"


class TestWriterStampCorrectness:
    """ft-version-01: a writer must stamp the minimum required version.

    ft-version-04: a writer that always stamps '1.0' is non-conformant
    even when the document happens to render correctly on readers.
    """

    def test_ft_version_01_matches_features_conforms(self):
        """A catdef using v1.3 subcats + range stamped '1.3' is writer-conformant."""
        data = _load("valid_stamp_matches_features.opencatalog")
        assert stamp_conforms(data)

    def test_ft_version_04_under_stamp_is_non_conformant(self):
        """A catdef using v1.3 features stamped '1.0' fails writer conformance."""
        data = _load("invalid_stamp_older_than_features.opencatalog")
        assert not stamp_conforms(data), (
            "Document using v1.3-era features but stamped 1.0 must fail "
            "writer-side stamp-conformance")
        # And required minimum should be 1.3 (range: true is the highest feature).
        assert required_minimum_version(data) == "1.3"


class TestWriterOverStamp:
    """Over-stamping is permitted but discouraged."""

    def test_over_stamp_conforms(self):
        """A catdef using only v1.0 features stamped '1.3' is writer-conformant."""
        data = _load("valid_stamp_newer_than_features.opencatalog")
        assert stamp_conforms(data)

    def test_over_stamp_minimum_is_lower_than_declared(self):
        """Over-stamping is detectable: declared > minimum required."""
        data = _load("valid_stamp_newer_than_features.opencatalog")
        declared = data["catdef"]
        required = required_minimum_version(data)
        assert _vtuple(declared) > _vtuple(required), (
            "Over-stamp fixture should have declared > required")


class TestReaderGracefulIgnore:
    """ft-version-02 / ft-version-03: reader graceful-ignore and optional warning.

    Readers MUST NOT reject a mis-stamped document; MAY warn.
    """

    def test_ft_version_02_reader_parses_understamped_document(self):
        """A reader given a mis-stamped document MUST parse without rejection.

        Reader-side parsing is modeled here as: validator runs without raising,
        and the document structure is still accessible. No stamp check gates.
        """
        data = _load("invalid_stamp_older_than_features.opencatalog")
        # Document loaded cleanly; basic invariants hold.
        assert data.get("catdef") == "1.0"
        assert data.get("product", {}).get("name")
        assert len(data.get("templates", [])) == 1
        # Reader is not obligated to reject solely because stamp < features.

    def test_ft_version_03_reader_may_warn_on_understamp(self):
        """A reader MAY surface a stamp-mismatch warning.

        The warning is advisory per §Versioning §Reader behavior. We test
        that a warning-emitter CAN detect the mismatch (i.e., the condition
        is machine-detectable), not that every reader MUST warn.
        """
        data = _load("invalid_stamp_older_than_features.opencatalog")
        # Warning condition: declared stamp < minimum required.
        declared = data.get("catdef", "1.0")
        required = required_minimum_version(data)
        warning_condition = _vtuple(declared) < _vtuple(required)
        assert warning_condition, (
            "Reader that wants to warn should detect declared < required")
