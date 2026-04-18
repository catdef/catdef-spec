# Proposal: Conformance validator shape coverage — close the v1.3 value-shape gap and formalize URL

**Status:** Draft
**Target version:** 1.4 (minor — formalizes `URL` value shape and extends the reference validator to enforce the full v1.3 value-shape surface)
**Origin:** [canonical/AUTHORING_FEEDBACK.md CA-006](../canonical/AUTHORING_FEEDBACK.md) (first-implementor feedback — the conformance suite rejects the canonical's spec-compliant value shapes)
**Conformance level affected:** Test-suite coverage across all levels (L1 through L4). No runtime behavior change — the spec-defined shapes are unchanged; the validator catches up to them.

## Summary

The reference conformance validator `validate_item_field_values()` in `conformance/test_field_values.py` does not recognize several value shapes that CATDEF_SPEC.md already defines. When run against the canonical ([`canonical/catalog.opencatalog`](../canonical/catalog.opencatalog)), it produces 22 false-positive errors against spec-compliant `Date` (circa/range), `Money` (range), `Number` (range), and `URL` (object) values. This proposal extends the validator to recognize those shapes, and formalizes the `URL` object schema in CATDEF_SPEC.md §Field Types (currently implied by prose — "A web URL with optional auto-extracted title, description, og:image" — but not schematized).

Scope is bounded to v1.3 shapes already in the spec plus the `URL` schema formalization. Polymorphic translatable-field validation (v1.4-draft) is out of scope here and belongs with the [i18n proposal's](i18n-polymorphic-fields.md) conformance test additions.

## Motivation

The canonical is the worked example every implementer tests against, and the conformance suite is the standard (value #4 — "the conformance suite is the standard"). When the suite's own reference validator flags the canonical as invalid, the four-artifact self-correcting loop inverts:

- **Spec prose** says Date values may be `{"date": "1850", "circa": true}` (§Date Type Extensions), that Number/Money/Date fields with `range: true` accept `{"min": N, "max": N}` / `{"low": {...}, "high": {...}}` / `{"start": "...", "end": "..."}` respectively (§Range Modifier), and that URL is "A web URL with optional auto-extracted title, description, og:image" (§Field Types).
- **Canonical** uses those shapes faithfully — 12 fields across 9 items exercise circa/range/URL-object.
- **Conformance suite** doesn't know about any of them. It expects `Date` / `URL` to be strings, `Money` to be `{"amount": N, "currency": "XXX"}`, `Number` to be a primitive.
- **Reference implementation** (future) will run the conformance suite against the canonical. Every run fails with 22 false positives on the bundle that is supposed to be the worked-correct example.

An implementer reading those failures will reach the wrong conclusion — "the canonical is broken" — and either fix it (wrong) or work around it (wrong). The correct conclusion — "the validator doesn't cover all the spec-defined shapes" — is invisible to them unless they chase the discrepancy through spec prose.

**Why `URL` gets a schema bump, not just a validator update.** The spec's prose mentions optional `title`, `description`, and `og:image` but doesn't formally describe the value as object-shaped. Implementations that emit URL objects (the canonical, Thingalog, and likely others) are doing so consistent with the prose but without a specified schema. Formalizing the schema is minor-level spec work. Without it, a validator extension to "accept URL objects" would need to hand-wave about what keys are permitted.

## Proposed change

### 1. Formalize `URL` object schema in CATDEF_SPEC.md §Field Types

Current prose (line ~446):

> | `URL` | Inline | A web URL with optional auto-extracted title, description, og:image |

Replace with a proper subsection after §GeoLocation Type or adjacent to §Date Type Extensions:

> ### URL Type
>
> `URL` stores a web address. The value may be either a plain string (the URL itself) or an object carrying the URL plus optional auto-extracted metadata.
>
> **Value shapes:**
>
> - String form: `"https://example.org/page"` — the minimal representation.
> - Object form:
>   ```json
>   {
>     "url": "https://example.org/page",
>     "title": "Page title",
>     "description": "Short description or og:description",
>     "og_image": "https://example.org/page/og.jpg"
>   }
>   ```
>
> **Keys (object form):**
>
> | Key | Type | Required | Description |
> |-----|------|----------|-------------|
> | `url` | string | yes | The actual URL. MUST be a valid HTTP/HTTPS URL. |
> | `title` | string | no | Page title, typically the `<title>` element or `og:title`. |
> | `description` | string | no | Short description, typically `<meta name="description">` or `og:description`. |
> | `og_image` | string | no | URL of a representative image, typically `og:image`. |
>
> Renderers MAY display the object form as a link preview card (favicon + title + description + image). When a URL field is presented for editing, the runtime MAY fetch and populate metadata on paste. Metadata fields are advisory — a runtime that cannot fetch them simply displays the URL string.
>
> **Round-trip behavior:** A catdef producer that receives the object form MUST preserve all keys on re-export. A catdef producer that has only a URL string SHOULD NOT fabricate metadata; the object form is used only when metadata is actually known.

### 2. Extend `validate_field_value()` in `conformance/test_field_values.py`

Add recognition of the following shapes. Pseudocode:

```python
def validate_field_value(label: str, value, fd: dict, values_map: dict) -> list[str]:
    errors = []
    ftype = fd.get("type")
    range_ok = fd.get("range") is True

    if ftype == "Date":
        # string: ISO-like
        if isinstance(value, str):
            pass  # existing check
        # circa object
        elif isinstance(value, dict) and "date" in value and value.get("circa") is True:
            if not isinstance(value["date"], str):
                errors.append(f"{label}: Date.circa value must carry a string 'date'")
        # range object (requires range: true on the field def)
        elif isinstance(value, dict) and "start" in value and "end" in value:
            if not range_ok:
                errors.append(f"{label}: Date range shape used but field def does not declare range: true")
            for k in ("start", "end"):
                if not isinstance(value.get(k), str):
                    errors.append(f"{label}: Date.range {k} must be a string")
        else:
            errors.append(f"{label}: expected Date value (string, circa object, or range object), got {type(value).__name__}")

    elif ftype == "Number":
        if range_ok and isinstance(value, dict):
            for k in ("min", "max"):
                if not isinstance(value.get(k), (int, float)) or isinstance(value.get(k), bool):
                    errors.append(f"{label}: Number range {k} must be a number")
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            pass  # existing check
        else:
            errors.append(f"{label}: expected Number (primitive, or range object with min/max)")

    elif ftype == "Money":
        if range_ok and isinstance(value, dict) and "low" in value and "high" in value:
            for side in ("low", "high"):
                obj = value[side]
                if not isinstance(obj, dict) or not isinstance(obj.get("amount"), (int, float)):
                    errors.append(f"{label}: Money.range.{side}.amount must be a number")
                if not isinstance(obj.get("currency"), str) or len(obj.get("currency", "")) != 3:
                    errors.append(f"{label}: Money.range.{side}.currency must be a 3-letter ISO code")
        elif isinstance(value, dict) and "amount" in value:
            # existing plain Money check
            if not isinstance(value["amount"], (int, float)):
                errors.append(f"{label}: Money.amount must be a number")
            if not isinstance(value.get("currency"), str) or len(value.get("currency", "")) != 3:
                errors.append(f"{label}: Money.currency must be a 3-letter ISO code")
        else:
            errors.append(f"{label}: expected Money ({{amount, currency}} or range {{low, high}})")

    elif ftype == "URL":
        if isinstance(value, str):
            pass  # plain URL string
        elif isinstance(value, dict):
            if not isinstance(value.get("url"), str):
                errors.append(f"{label}: URL object must carry a string 'url'")
            for k in ("title", "description", "og_image"):
                if k in value and not isinstance(value[k], str):
                    errors.append(f"{label}: URL.{k} must be a string")
        else:
            errors.append(f"{label}: expected URL (string or object with url/title/description/og_image)")

    # ... existing String, Integer, RichText, Enumerated, Photo, Table, CloudFile, Boolean, GeoLocation checks unchanged
    return errors
```

### 3. Document validator-coverage guarantee in conformance/README.md

Add a paragraph to `conformance/README.md` clarifying that the reference validator MUST recognize every value shape defined by the current spec version, and that shape-gap discovery (e.g., a catdef that the spec says is valid but the validator rejects) is a suite bug, not a catdef bug.

## Backward compatibility

**Existing catdefs:**
- String-form Date / URL: still accepted — the validator adds object-shape recognition, doesn't replace string-shape recognition.
- Flat Money: still accepted — range Money is a separate shape gated on `range: true`.
- Simple Number: still accepted — range Number likewise.

**Existing runtimes:**
- Any runtime that already implements the v1.3 shape surface (any L2+ runtime must, to be conformant) is unaffected. The validator is catching up to them, not the other way around.
- Runtimes that never encountered the range/circa/URL-object shapes because their authors worked against the validator: these will now see conformance-suite failures that match the underlying shape support, which is correct behavior.

**Migration:** None. The validator change is additive; prior valid catdefs remain valid.

## Conformance tests

Extend `conformance/fixtures/valid_all_field_types.opencatalog` (or add a sibling `valid_v13_value_shapes.opencatalog`) to cover:

- A `Date` field with circa value: `{"date": "1905", "circa": true}`
- A `Date` field with range value on a `range: true` field def
- A `Money` field with range value on a `range: true` field def
- A `Number` field with range value on a `range: true` field def
- A `URL` field with object value carrying all four keys

Add tests to `conformance/test_field_values.py`:

- **ft-shape-01**: `valid_v13_value_shapes.opencatalog` validates without errors.
- **ft-shape-02**: A Date circa object missing the `date` key is rejected.
- **ft-shape-03**: A Date range object missing `start` or `end` is rejected.
- **ft-shape-04**: A Money range object where `low`/`high` aren't both proper Money objects is rejected.
- **ft-shape-05**: A Number range object with non-numeric `min`/`max` is rejected.
- **ft-shape-06**: A URL object without a `url` key is rejected; a URL object with an integer `title` is rejected.
- **ft-shape-07**: The canonical (`canonical/catalog.opencatalog`) validates without errors under the extended validator. This is the regression test that prevents the gap from reopening — if the canonical goes out of sync with the validator, either the canonical is wrong (shape bug) or the validator is wrong (coverage bug).

ft-shape-07 is the most important of the seven — it makes the canonical a self-checking artifact of the conformance suite.

## Alternatives considered

### A. Leave the validator as-is; document the gap in conformance/README.md

Rejected. The validator is the reference implementation of conformance checking. Documenting its limitations in prose without fixing them shifts the burden to every downstream implementer (who must read the prose, understand what to expect, and work around it). Also inconsistent with value #4 — the suite is the standard; an incomplete standard produces incomplete conformance.

### B. Treat URL's object shape as an extension-namespace feature (`x.<domain>.url_preview`)

Rejected. URL with auto-extracted metadata is already described in core CATDEF_SPEC.md prose; moving it to `x.` after the fact is a breaking change for anyone already emitting the shape (including the canonical, Thingalog, and Thingalog-descended implementations). Formalization in core is less disruptive than a post-hoc extension-namespace relegation.

### C. Expand scope to include polymorphic-translatable-field validation

Rejected for this proposal. Polymorphic fields are a v1.4-draft feature (per the i18n proposal), and their validator logic should land with that proposal's conformance-test additions. Bundling them here would conflate two separate scopes and create merge coordination overhead. The i18n proposal already sketches the polymorphic-field validation at a conceptual level in its `ft-i18n-*` tests; implementation belongs there.

### D. Skip `URL` schema formalization; only extend the validator

Rejected. Without a formalized schema, a validator that "accepts URL objects" has no specified set of allowed keys. An implementer could legitimately emit `{"url": "...", "href": "..."}` thinking either key is fine. The formalization is a small prose addition and closes the ambiguity.

## Open questions

1. **`og_image` vs. `og:image`.** The spec prose uses `og:image` (the actual Open Graph property name with a colon). The proposed object-shape key is `og_image` (underscore), since JSON keys with colons require escaping and conventionally JSON schemas use underscores. Is there a reason to prefer the colon form? Recommendation: `og_image` for JSON ergonomics; cite `og:image` as the source in the key's description.

2. **Validator enforcement of URL format.** Should `validate_field_value` also enforce that `url` is a valid HTTP/HTTPS URL (basic `urlparse` check), or leave that to runtime concerns? Recommendation: do a lightweight `startswith("http://") or startswith("https://")` check to catch obviously-wrong values. Deeper validation (DNS, reachability) stays a runtime concern.

3. **Range on non-declared range fields.** Today, a Money field without `range: true` that receives `{"low": ..., "high": ...}` silently fails (or worse, silently accepts as a flat Money). Should the validator reject this as a shape/field-def mismatch? Recommendation: yes, reject explicitly — the `range` attribute is load-bearing, and a shape-def mismatch is always a bug.

4. **Relationship to the v1.4 bundle release-management constraint.** This proposal is scoped to v1.3 shape coverage plus a small URL formalization. Does it need to bundle with CA-001/002/003 and the i18n/MCP proposals? Recommendation: **no bundle lock** — this proposal is validator work, not runtime-behavior change. It can ship as a v1.4 minor alongside the bundle without interlock, because existing catdefs don't become invalid and existing runtimes don't become non-conformant. The main bundle can merge with or without this one.

## Requested maintainer actions

- Sign off on formalizing the `URL` object schema in CATDEF_SPEC.md §Field Types (the URL Type subsection above).
- Sign off on extending `validate_field_value()` for Date circa/range, Money range, Number range, and URL object shapes.
- Confirm target version: 1.4 (minor) per the precedent of CA-001/002/003, or 1.3.1 (patch) since the runtime-behavior surface is unchanged. My read: 1.4 because the URL formalization is a new normative schema, not a pure validator catch-up.
- Confirm polymorphic-translatable-field validation is out of scope here and belongs with the i18n proposal's conformance tests.
- Confirm `og_image` (underscore) as the JSON-form key for the Open Graph image.
- Sign off on `ft-shape-07` — the regression test that validates the canonical itself. This is the artifact that makes "canonical and conformance suite drift apart" structurally detectable.
