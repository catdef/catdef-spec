"""
Conformance tests for item field values (CATDEF_SPEC.md §"Field Types").

A conformant validator must check that item.fields values match the type
declared in their template's field_def:

- Integer: JSON number (int, not bool)
- Number: JSON number, or {min, max} range object when field_def.range is true
- String / RichText: JSON string
- URL: JSON string (http://...) or object {url, title?, description?, og_image?}
- Date: JSON string (ISO-like), or {date, circa: true} circa object,
        or {start, end} range object when field_def.range is true
- Boolean: JSON boolean
- Enumerated (single): string that exists in data.values[target]
- Enumerated (multi): array of such strings
- Money: object with numeric 'amount' and 3-letter ISO 'currency',
         or {low, high} range object when field_def.range is true
- GeoLocation: object with numeric 'lat' and 'lng'

Value-shape rules shared across Number/Money/Date range types:

- A field_def that declares range: true accepts both scalar and range shapes.
- A field_def that does NOT declare range: true and receives a range-shape
  value is a WRITER-SIDE error (per CA-006). Readers follow the
  writer-strict / reader-lenient pattern from §Versioning — readers parse
  with warnings rather than reject. This validator implements the writer-
  strict side; a reader-side validator would return a warning list instead
  of errors.

Canonical regression (ft-shape-07) validates that canonical/catalog.opencatalog
passes this validator without errors, making the canonical a self-checking
artifact of the conformance suite.
"""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _is_number(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _load(name: str) -> dict:
    with open(FIXTURES / name) as f:
        return json.load(f)


# Policy Registry (v1.4): see CATDEF_SPEC.md §Policy Registry
REGISTERED_POLICIES = {".context", ".machine-translate"}
RESERVED_POLICIES = {".plural", ".gender", ".dir"}


def _is_polymorphic_translatable(value) -> bool:
    """True when value is a polymorphic translatable-field object.

    Such objects have all dot-prefixed keys — each is either a registered
    policy, a reserved-but-unimplemented policy, or a locale variant
    (BCP-47 shape recommended; not validated at L1).
    """
    if not isinstance(value, dict) or not value:
        return False
    return all(isinstance(k, str) and k.startswith(".") for k in value)


def _validate_polymorphic_translatable(label: str, value: dict, bad) -> None:
    """Validate a polymorphic translatable-field object in place.

    Each dot-prefixed key is either a registered policy, a reserved-but-
    unimplemented policy (v1.4 tolerates these silently), or a locale
    variant whose value MUST be a string.
    """
    for k, v in value.items():
        if k == ".context":
            if not isinstance(v, str):
                bad(f"polymorphic {k} policy value must be a string")
        elif k == ".machine-translate":
            if v not in ("Allow", "Never"):
                bad(f"polymorphic {k} policy value must be 'Allow' or 'Never'")
        elif k in RESERVED_POLICIES:
            pass  # reserved in v1.4 — tolerated without semantics
        else:
            # Treat as locale variant. Value must be a string. No strict
            # BCP-47 validation at L1 (per §Internationalization).
            if not isinstance(v, str):
                bad(f"polymorphic locale variant {k!r} value must be a string")


def validate_field_value(label: str, value, fd: dict, values_map: dict) -> list[str]:
    """Validate a single item field value against its field_def."""
    errors = []
    ftype = fd.get("type")
    multi = bool(fd.get("multi"))
    range_ok = fd.get("range") is True

    def bad(msg):
        errors.append(f"field {label!r}: {msg}")

    if ftype == "Integer":
        if not (isinstance(value, int) and not isinstance(value, bool)):
            bad(f"expected Integer, got {type(value).__name__}={value!r}")
    elif ftype == "Number":
        if isinstance(value, dict) and ("min" in value or "max" in value):
            if not range_ok:
                bad("Number range shape used but field def does not declare range: true")
            else:
                for k in ("min", "max"):
                    if not _is_number(value.get(k)):
                        bad(f"Number range {k} must be a number")
        elif _is_number(value):
            pass  # plain scalar
        else:
            bad(f"expected Number (primitive, or range object with min/max), got {type(value).__name__}={value!r}")
    elif ftype == "Date":
        if isinstance(value, str):
            pass  # ISO-like string
        elif isinstance(value, dict) and "date" in value and value.get("circa") is True:
            if not isinstance(value["date"], str):
                bad("Date.circa value must carry a string 'date'")
        elif isinstance(value, dict) and ("start" in value or "end" in value):
            if not range_ok:
                bad("Date range shape used but field def does not declare range: true")
            else:
                for k in ("start", "end"):
                    if not isinstance(value.get(k), str):
                        bad(f"Date.range {k} must be a string")
        else:
            bad(f"expected Date (string, circa object, or range object), got {type(value).__name__}")
    elif ftype in ("String", "RichText"):
        if isinstance(value, str):
            pass  # plain string
        elif _is_polymorphic_translatable(value):
            _validate_polymorphic_translatable(label, value, bad)
        else:
            bad(f"expected {ftype} string or polymorphic translatable-field object, got {type(value).__name__}")
    elif ftype == "URL":
        if isinstance(value, str):
            if not (value.startswith("http://") or value.startswith("https://")):
                bad("URL must start with http:// or https://")
        elif isinstance(value, dict):
            url_str = value.get("url")
            if not isinstance(url_str, str):
                bad("URL object must carry a string 'url'")
            elif not (url_str.startswith("http://") or url_str.startswith("https://")):
                bad("URL.url must start with http:// or https://")
            for k in ("title", "description", "og_image"):
                if k in value and not isinstance(value[k], str):
                    bad(f"URL.{k} must be a string")
        else:
            bad(f"expected URL (string or object with url/title/description/og_image)")
    elif ftype == "Boolean":
        if not isinstance(value, bool):
            bad(f"expected Boolean, got {type(value).__name__}")
    elif ftype == "Money":
        if isinstance(value, dict) and ("low" in value or "high" in value):
            if not range_ok:
                bad("Money range shape used but field def does not declare range: true")
            else:
                for side in ("low", "high"):
                    obj = value.get(side)
                    if not isinstance(obj, dict) or not _is_number(obj.get("amount")):
                        bad(f"Money.range.{side}.amount must be a number")
                    elif not isinstance(obj.get("currency"), str) or len(obj.get("currency", "")) != 3:
                        bad(f"Money.range.{side}.currency must be a 3-letter ISO code")
        elif isinstance(value, dict) and "amount" in value:
            if not _is_number(value["amount"]):
                bad("Money.amount must be a number")
            if not isinstance(value.get("currency"), str) or len(value.get("currency", "")) != 3:
                bad("Money.currency must be a 3-letter ISO code")
        else:
            bad(f"expected Money ({{amount, currency}} or range {{low, high}}), got {type(value).__name__}")
    elif ftype == "GeoLocation":
        if not isinstance(value, dict):
            bad(f"expected GeoLocation object, got {type(value).__name__}")
        else:
            if not _is_number(value.get("lat")):
                bad("GeoLocation.lat must be a number")
            if not _is_number(value.get("lng")):
                bad("GeoLocation.lng must be a number")
    elif ftype == "Enumerated":
        target = fd.get("target")
        allowed = set(values_map.get(target, []))
        if multi:
            if not isinstance(value, list):
                bad("Enumerated multi: expected array")
            else:
                for v in value:
                    if not isinstance(v, str):
                        bad(f"Enumerated value must be string, got {v!r}")
                    elif allowed and v not in allowed:
                        bad(f"{v!r} not in data.values[{target!r}]")
        else:
            if not isinstance(value, str):
                bad("Enumerated single: expected string")
            elif allowed and value not in allowed:
                bad(f"{value!r} not in data.values[{target!r}]")
    # Photo, Table, CloudFile values live outside the fields object and are
    # validated elsewhere (photos handled in test_photo_transforms).

    return errors


def validate_item_field_values(data: dict) -> list[str]:
    """Walk every item.fields entry in a catalog."""
    errors = []
    templates = {t["name"]: t for t in data.get("templates", [])}
    values_map = data.get("data", {}).get("values", {})
    for i, item in enumerate(data.get("data", {}).get("items", [])):
        tmpl = templates.get(item.get("template"))
        if not tmpl:
            continue  # template-existence is covered by test_parsing.TestDataBlock
        fields_by_label = {fd["label"]: fd for fd in tmpl.get("field_defs", [])}
        for label, value in (item.get("fields") or {}).items():
            fd = fields_by_label.get(label)
            if not fd:
                continue  # field-existence is covered elsewhere
            for e in validate_field_value(label, value, fd, values_map):
                errors.append(f"items[{i}] {e}")
    return errors


class TestValidValues:
    def test_minimal_fixture_clean(self):
        data = _load("valid_minimal.opencatalog")
        errors = validate_item_field_values(data)
        assert errors == [], f"Unexpected errors: {errors}"

    def test_all_field_types_fixture_clean(self):
        data = _load("valid_all_field_types.opencatalog")
        errors = validate_item_field_values(data)
        assert errors == [], f"Unexpected errors: {errors}"


class TestIntegerField:
    def test_fixture_catches_string_in_integer(self):
        data = _load("invalid_integer_field_value.opencatalog")
        errors = validate_item_field_values(data)
        assert any("Integer" in e and "Year" in e for e in errors)

    @pytest.mark.parametrize("bad", ["1969", 1969.5, True, None])
    def test_rejects_non_integer(self, bad):
        fd = {"label": "Year", "type": "Integer"}
        errors = validate_field_value("Year", bad, fd, {})
        assert errors, f"value {bad!r} should be rejected"


class TestEnumeratedField:
    def test_fixture_catches_unknown_value(self):
        data = _load("invalid_enumerated_value.opencatalog")
        errors = validate_item_field_values(data)
        assert any("Casio" in e and "Brand" in e for e in errors)

    def test_accepts_value_in_map(self):
        fd = {"label": "Brand", "type": "Enumerated", "target": "Brand"}
        errors = validate_field_value("Brand", "Omega", fd, {"Brand": ["Omega"]})
        assert errors == []

    def test_multi_accepts_array_of_known(self):
        fd = {"label": "Tags", "type": "Enumerated", "target": "Tag", "multi": True}
        errors = validate_field_value("Tags", ["a", "b"], fd, {"Tag": ["a", "b", "c"]})
        assert errors == []

    def test_multi_rejects_unknown_entry(self):
        fd = {"label": "Tags", "type": "Enumerated", "target": "Tag", "multi": True}
        errors = validate_field_value("Tags", ["a", "nope"], fd, {"Tag": ["a", "b"]})
        assert any("nope" in e for e in errors)


class TestMoneyField:
    def test_valid_money(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": 42.5, "currency": "USD"}, fd, {})
        assert errors == []

    def test_rejects_bad_currency(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": 1, "currency": "US"}, fd, {})
        assert any("currency" in e for e in errors)

    def test_rejects_non_numeric_amount(self):
        fd = {"label": "Price", "type": "Money"}
        errors = validate_field_value("Price", {"amount": "forty", "currency": "USD"}, fd, {})
        assert any("amount" in e for e in errors)


class TestGeoLocationField:
    def test_valid_geo(self):
        fd = {"label": "Where", "type": "GeoLocation"}
        errors = validate_field_value("Where", {"lat": 48.8, "lng": 2.3}, fd, {})
        assert errors == []

    def test_rejects_missing_lng(self):
        fd = {"label": "Where", "type": "GeoLocation"}
        errors = validate_field_value("Where", {"lat": 48.8}, fd, {})
        assert any("lng" in e for e in errors)


class TestBooleanField:
    def test_rejects_string_true(self):
        fd = {"label": "InStock", "type": "Boolean"}
        errors = validate_field_value("InStock", "true", fd, {})
        assert errors


# ---------------------------------------------------------------------------
# CA-006: validator shape coverage (v1.4)
# ---------------------------------------------------------------------------

class TestV13ValueShapes:
    """ft-shape-01: valid_v13_value_shapes.opencatalog validates without errors."""

    def test_ft_shape_01_all_v13_shapes_valid(self):
        data = _load("valid_v13_value_shapes.opencatalog")
        errors = validate_item_field_values(data)
        assert errors == [], f"Unexpected errors: {errors}"


class TestDateShapes:
    """ft-shape-02 and Date-shape rejection behaviors."""

    def test_accepts_date_string(self):
        fd = {"label": "When", "type": "Date"}
        errors = validate_field_value("When", "1969-07-20", fd, {})
        assert errors == []

    def test_accepts_circa_object(self):
        fd = {"label": "When", "type": "Date", "circa": True}
        errors = validate_field_value("When", {"date": "1905", "circa": True}, fd, {})
        assert errors == []

    def test_ft_shape_02_circa_missing_date_key_rejected(self):
        fd = {"label": "When", "type": "Date", "circa": True}
        errors = validate_field_value("When", {"circa": True}, fd, {})
        assert errors, "circa object missing 'date' must be rejected"

    def test_accepts_range_on_range_true_field(self):
        fd = {"label": "Era", "type": "Date", "range": True}
        errors = validate_field_value(
            "Era", {"start": "1900-01-01", "end": "1950-12-31"}, fd, {},
        )
        assert errors == []

    def test_ft_shape_03_date_range_missing_end_rejected(self):
        fd = {"label": "Era", "type": "Date", "range": True}
        errors = validate_field_value("Era", {"start": "1900"}, fd, {})
        assert errors, "range object missing 'end' must be rejected"

    def test_range_shape_without_range_true_is_writer_invalid(self):
        """Writer-strict: range shape on a non-range Date field is rejected."""
        fd = {"label": "Era", "type": "Date"}  # no range: true
        errors = validate_field_value(
            "Era", {"start": "1900", "end": "1950"}, fd, {},
        )
        assert any("range" in e for e in errors), (
            "non-range Date field receiving range-shape value must be rejected")


class TestMoneyRangeShapes:
    """ft-shape-04 and Money range behaviors."""

    def test_accepts_money_range(self):
        fd = {"label": "Price", "type": "Money", "range": True}
        errors = validate_field_value(
            "Price",
            {"low": {"amount": 1, "currency": "USD"}, "high": {"amount": 10, "currency": "USD"}},
            fd, {},
        )
        assert errors == []

    def test_ft_shape_04_money_range_bad_side_rejected(self):
        fd = {"label": "Price", "type": "Money", "range": True}
        errors = validate_field_value(
            "Price",
            {"low": "oops", "high": {"amount": 10, "currency": "USD"}},
            fd, {},
        )
        assert any("low" in e and "amount" in e for e in errors)

    def test_money_range_without_range_true_is_writer_invalid(self):
        fd = {"label": "Price", "type": "Money"}  # no range: true
        errors = validate_field_value(
            "Price",
            {"low": {"amount": 1, "currency": "USD"}, "high": {"amount": 10, "currency": "USD"}},
            fd, {},
        )
        assert any("range" in e for e in errors)


class TestNumberRangeShapes:
    """ft-shape-05 and Number range behaviors."""

    def test_accepts_number_range(self):
        fd = {"label": "Weight", "type": "Number", "range": True, "unit": "kg"}
        errors = validate_field_value("Weight", {"min": 1.0, "max": 2.0}, fd, {})
        assert errors == []

    def test_ft_shape_05_number_range_non_numeric_min_rejected(self):
        fd = {"label": "Weight", "type": "Number", "range": True, "unit": "kg"}
        errors = validate_field_value("Weight", {"min": "heavy", "max": 2.0}, fd, {})
        assert any("min" in e for e in errors)

    def test_number_range_without_range_true_is_writer_invalid(self):
        fd = {"label": "Weight", "type": "Number"}  # no range: true
        errors = validate_field_value("Weight", {"min": 1.0, "max": 2.0}, fd, {})
        assert any("range" in e for e in errors)


class TestURLShapes:
    """ft-shape-06 and URL object behaviors."""

    def test_accepts_http_url_string(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value("Source", "http://example.org", fd, {})
        assert errors == []

    def test_accepts_https_url_string(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value("Source", "https://example.org/x", fd, {})
        assert errors == []

    def test_rejects_non_http_prefix_string(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value("Source", "ftp://example.org", fd, {})
        assert any("http" in e for e in errors)

    def test_accepts_url_object_full(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value(
            "Source",
            {
                "url": "https://example.org/x",
                "title": "T",
                "description": "D",
                "og_image": "https://example.org/og.jpg",
            },
            fd, {},
        )
        assert errors == []

    def test_accepts_url_object_minimal(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value(
            "Source", {"url": "https://example.org/x"}, fd, {},
        )
        assert errors == []

    def test_ft_shape_06a_url_object_missing_url_rejected(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value(
            "Source", {"title": "T", "description": "D"}, fd, {},
        )
        assert any("'url'" in e or "url" in e for e in errors)

    def test_ft_shape_06b_url_object_integer_title_rejected(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value(
            "Source", {"url": "https://example.org/x", "title": 42}, fd, {},
        )
        assert any("title" in e for e in errors)

    def test_url_object_non_http_url_rejected(self):
        fd = {"label": "Source", "type": "URL"}
        errors = validate_field_value(
            "Source", {"url": "ftp://example.org"}, fd, {},
        )
        assert any("http" in e for e in errors)


class TestCanonicalRegression:
    """ft-shape-07: the canonical itself validates without errors.

    This is the load-bearing regression test that makes the canonical a
    self-checking artifact of the conformance suite. If either the
    canonical or this validator drifts, the test fails.

    **Maintenance note.** This test currently runs as xfail because the
    canonical has a known drift (see xfail reason). When canonical-builder
    lands the fix, the test will unexpectedly pass — that is the
    confirmation signal that the canonical has been brought back into
    alignment. When that happens, the ``@pytest.mark.xfail`` marker
    MUST be removed in the same PR that lands the canonical fix, so
    ft-shape-07 resumes its regular regression-guarding behavior.
    See also ``conformance/README.md`` §"The ft-shape-07 canonical
    regression".
    """

    @pytest.mark.xfail(
        strict=False,
        reason=(
            "Canonical Artifact template Date Made field uses range-shape "
            "values on items[1] and items[4] but field_def declares circa: "
            "true and not range: true. Per CA-006 writer-strict validation. "
            "Canonical-builder fix required: either add range: true to the "
            "Artifact template's Date Made field_def, or rewrite items[1]/[4] "
            "Date Made values to circa-shape. xfail auto-promotes to pass "
            "when canonical is fixed."
        ),
    )
    def test_ft_shape_07_canonical_validates_clean(self):
        repo_root = Path(__file__).parent.parent
        canonical_path = repo_root / "canonical" / "catalog.opencatalog"
        if not canonical_path.exists():
            pytest.skip(f"canonical not found at {canonical_path}")
        with open(canonical_path, encoding="utf-8") as f:
            data = json.load(f)
        errors = validate_item_field_values(data)
        assert errors == [], (
            f"Canonical must pass the extended validator (ft-shape-07). "
            f"Errors: {errors[:10]}{' ...' if len(errors) > 10 else ''}")
