"""
catdef Conformance: subcat value resolution tests (CA-003).

Per CATDEF_SPEC.md §Subcats §Value resolution:

- When subcats.<target>.values is declared, it is AUTHORITATIVE for the
  Enumerated namespace <target>. The set of keys is the complete namespace.
- data.values.<target> is OPTIONAL. A writer MAY include it as a SUBSET
  for L1-runtime ergonomics (pre-declared namespace visibility).
- Writer MUST NOT emit data.values.<target> names that are not keys of
  subcats.<target>.values (superset is writer-invalid).
- Reader MUST NOT reject on superset; MAY warn; resolves namespace from
  subcats keys only. (Writer-strict / reader-lenient asymmetry, mirror
  of §Versioning and the polymorphic-field unknown-key rule.)
- When NO subcat is declared for <target>, data.values.<target> is the
  authoritative bare-name list.
- Empty-seed pattern (subcats.<target> with field_defs but no values,
  paired with data.values.<target>) is valid — data.values supplies the
  names; subcat field_defs apply when enrichment is attached later.

Shared namespaces: a subcat's value namespace is shared across all
references to the same target name.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


def resolve_namespace(data: dict, target: str) -> tuple[set[str], list[str]]:
    """Resolve the Enumerated namespace <target> per CA-003.

    Returns (namespace, warnings). namespace is the authoritative set of
    value names; warnings lists any reader-lenient notices (e.g., superset
    detected, unknown data.values entries).
    """
    subcats = data.get("subcats", {})
    data_values = data.get("data", {}).get("values", {})

    subcat = subcats.get(target) if isinstance(subcats, dict) else None
    subcat_values = (subcat or {}).get("values") if isinstance(subcat, dict) else None
    dv_list = data_values.get(target) if isinstance(data_values, dict) else None

    warnings: list[str] = []

    # Case 1: subcat declared with seeded values → authoritative.
    if subcat is not None and isinstance(subcat_values, dict):
        namespace = set(subcat_values.keys())
        if isinstance(dv_list, list):
            extras = [n for n in dv_list if n not in namespace]
            if extras:
                warnings.append(
                    f"data.values[{target!r}] contains {extras!r} not in "
                    f"subcats[{target!r}].values — reader ignores; writer-side invalid"
                )
        return namespace, warnings

    # Case 2: empty-seed pattern — subcat with field_defs but no values,
    # paired with data.values.
    if subcat is not None and subcat_values is None and isinstance(dv_list, list):
        return set(dv_list), warnings

    # Case 3: no subcat declared → data.values is authoritative.
    if subcat is None and isinstance(dv_list, list):
        return set(dv_list), warnings

    # Case 4: nothing declared — empty namespace.
    return set(), warnings


def writer_validate_subcat_superset(data: dict) -> list[str]:
    """Writer-side validation: report data.values entries not in subcats keys.

    Returns a list of error messages. An empty list means writer-conformant.
    """
    errors: list[str] = []
    subcats = data.get("subcats", {})
    data_values = data.get("data", {}).get("values", {})
    if not isinstance(subcats, dict) or not isinstance(data_values, dict):
        return errors
    for target, subcat in subcats.items():
        if not isinstance(subcat, dict):
            continue
        subcat_values = subcat.get("values")
        dv_list = data_values.get(target)
        if isinstance(subcat_values, dict) and isinstance(dv_list, list):
            extras = [n for n in dv_list if n not in subcat_values]
            if extras:
                errors.append(
                    f"data.values[{target!r}] contains {extras!r} not in "
                    f"subcats[{target!r}].values (writer-invalid per CA-003 superset rule)"
                )
    return errors


class TestSubcatValuesOnly:
    """ft-subcat-values-01: subcats.Brand.values authoritative; no data.values.Brand."""

    def test_ft_subcat_values_01_resolves_from_subcats_keys(self):
        data = _load("valid_subcat_values_only.opencatalog")
        namespace, warnings = resolve_namespace(data, "Brand")
        assert namespace == {"Omega", "Rolex"}
        assert warnings == []

    def test_items_reference_valid_brand_values(self):
        data = _load("valid_subcat_values_only.opencatalog")
        namespace, _ = resolve_namespace(data, "Brand")
        for item in data["data"]["items"]:
            brand = item["fields"]["Brand"]
            assert brand in namespace


class TestSubcatPlusMatchingDataValues:
    """ft-subcat-values-02: both forms match; redundant data.values does not change state."""

    def test_ft_subcat_values_02_same_resolution_as_subcat_only(self):
        data_both = _load("valid_subcat_plus_matching_data_values.opencatalog")
        data_subcat_only = _load("valid_subcat_values_only.opencatalog")
        ns_both, warn_both = resolve_namespace(data_both, "Brand")
        ns_only, _ = resolve_namespace(data_subcat_only, "Brand")
        assert ns_both == ns_only == {"Omega", "Rolex"}
        assert warn_both == []  # data.values is a subset of subcats keys → no warning

    def test_writer_side_validator_accepts_matching(self):
        """Legacy pattern with matching names passes writer-side validation."""
        data = _load("valid_subcat_plus_matching_data_values.opencatalog")
        assert writer_validate_subcat_superset(data) == []


class TestDataValuesOnly:
    """ft-subcat-values-03: Enumerated field without subcat resolves from data.values."""

    def test_ft_subcat_values_03_resolves_from_data_values(self):
        data = _load("valid_data_values_only.opencatalog")
        namespace, warnings = resolve_namespace(data, "Condition")
        assert namespace == {"Mint", "Excellent", "Very Good", "Good"}
        assert warnings == []

    def test_items_reference_valid_condition_values(self):
        data = _load("valid_data_values_only.opencatalog")
        namespace, _ = resolve_namespace(data, "Condition")
        for item in data["data"]["items"]:
            cond = item["fields"]["Condition"]
            assert cond in namespace


class TestSupersetAsymmetry:
    """ft-subcat-values-04a (writer-side) and -04b (reader-side).

    CA-003 writer-strict / reader-lenient asymmetry.
    """

    def test_ft_subcat_values_04a_writer_rejects_superset(self):
        """Writer-side validator MUST reject invalid_data_values_superset.opencatalog."""
        data = _load("invalid_data_values_superset.opencatalog")
        errors = writer_validate_subcat_superset(data)
        assert errors, "writer-side validator must reject superset"
        # The extra name is Rolex (subcat only has Omega).
        assert any("Rolex" in e for e in errors)

    def test_ft_subcat_values_04b_reader_parses_without_refusal(self):
        """Reader MUST parse the superset fixture without refusal; MAY warn.

        Reader-side: resolve_namespace never raises; returns the subcats-only
        namespace and a warning about the superset entry.
        """
        data = _load("invalid_data_values_superset.opencatalog")
        namespace, warnings = resolve_namespace(data, "Brand")
        # Resolved namespace is subcats keys only — "Rolex" is NOT included.
        assert namespace == {"Omega"}
        # Warning MAY appear — the helper implements the MAY by always
        # surfacing it. A reader may emit or suppress the warning per its
        # own UX; this test checks the warning is detectable.
        assert any("Rolex" in w for w in warnings)

    def test_items_only_reference_resolved_namespace(self):
        """The superset fixture's items reference only Omega; Rolex in
        data.values is ignored by the resolver. Items validate cleanly."""
        data = _load("invalid_data_values_superset.opencatalog")
        namespace, _ = resolve_namespace(data, "Brand")
        for item in data["data"]["items"]:
            assert item["fields"]["Brand"] in namespace


class TestEmptySubcatPlusDataValues:
    """ft-subcat-values-05: empty-seed pattern."""

    def test_ft_subcat_values_05_empty_subcat_resolves_from_data_values(self):
        data = _load("valid_empty_subcat_plus_data_values.opencatalog")
        namespace, warnings = resolve_namespace(data, "Brand")
        assert namespace == {"Omega", "Rolex"}
        assert warnings == []

    def test_empty_subcat_field_defs_available_for_later_enrichment(self):
        """The subcat has field_defs (Country, Founded) available even though
        values aren't seeded; runtime can attach enrichment later."""
        data = _load("valid_empty_subcat_plus_data_values.opencatalog")
        subcat = data["subcats"]["Brand"]
        assert "values" not in subcat or subcat.get("values") in (None, {}), (
            "empty-seed pattern: subcat has no values at load time")
        labels = {fd["label"] for fd in subcat["field_defs"]}
        assert labels == {"Country", "Founded"}
