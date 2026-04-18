# AUTHORING_FEEDBACK.md

Spec friction encountered while authoring the canonical file. Each item below is a question or ambiguity that surfaced during construction — the kind of thing the "first implementer" would file through the normal feedback channel (`catdef.org/feedback`) once that endpoint exists, per [CLAUDE.md](../CLAUDE.md)'s "every implementation files feedback like any other consumer" rule.

These are **not** proposals or spec amendments. They are reports. The catdef-maintainer role handling canonical-file authorship also holds maintainer authority over the spec prose, but this file exists to respect the structural boundary — one role wears one hat at a time, and when the canonical-author hat encounters spec friction, it files a report rather than editing the spec in-flight.

The catdef maintainers may triage these at their discretion.

## Items

### CA-001 — Outer archive extension for ZIP-bundled CATIO

**Severity:** clarification

**What the spec says:**

- [CATIO_SPEC.md §Structure](../CATIO_SPEC.md) shows the example:
  ```
  catalog-export.zip
  ├── catalog.opencatalog
  ├── photos/
  ```
  The outer archive is `.zip`; the inner JSON is `.opencatalog`.

- The [MCP conformance proposal](../proposals/mcp-conformance-levels-and-reference.md) references "a single `.opencatalog` bundle" and proposes a filename like `canonical/welch-arctic-collection.opencatalog` — an outer file with the `.opencatalog` extension that is expected to be a ZIP.

**The question:** When a CATIO document is packaged as a ZIP bundle with photos, what is the outer archive's extension? The spec prose has not reconciled this — the example diagram says `.zip`, the MCP proposal says `.opencatalog`.

**Why it matters:** Importers decide how to process a file based on extension. If both `.zip` and `.opencatalog` are permitted for a bundled archive, importers must content-sniff (check for a ZIP signature + look for a `.opencatalog` at the archive root). If only one is permitted, the spec should say which.

**Current canonical choice (pending guidance):** The canonical outer archive is named `riverside-heritage-reference-v1.4.opencatalog` — matching the MCP proposal's naming pattern. If the spec clarifies toward `.zip` as the outer, the canonical will be renamed.

### CA-002 — `primaryLocale` declared in a document stamped `"catdef": "1.3"`

**Severity:** clarification

**What the spec says:**

- `primaryLocale` is introduced by the [i18n proposal](../proposals/i18n-polymorphic-fields.md) as a v1.4 top-level field.
- Value #5 (forward compatibility) says old runtimes gracefully ignore new fields.

**The question:** If a catdef document declares `"catdef": "1.3"` and also `"primaryLocale": "en"`, what is the expected behavior? Options:

1. **Accept.** The field is forward-compatible; a v1.4 runtime reads it, a v1.3 runtime ignores it.
2. **Warn.** Emit a forward-compatibility warning; accept the document.
3. **Reject.** The `catdef` version stamp should match the features used.

The canonical deliberately tests a v1.4-aware document (`"catdef": "1.4"` — aspirational since v1.4 isn't released yet); this question is about the converse edge case — mixed-version documents.

**Why it matters:** Tooling that auto-updates catdef versions during import (e.g., Thingalog's import pipeline) needs to know whether to silently upgrade the `catdef` stamp, warn, or refuse.

### CA-003 — `data.values` bare-name list vs. `subcats.<name>.values` enriched object

**Severity:** clarification

**What the spec says:**

- [CATDEF_SPEC.md §Subcats](../CATDEF_SPEC.md) shows that seeded values appear inside `subcats.<name>.values` as an object `{name: {field: value, …}}`.
- The watches sample ([`samples/watches.opencatalog`](../samples/watches.opencatalog)) places a bare-name array under `data.values.<name>` — the value names without enrichment.
- The CATDEF_SPEC.md prose doesn't explicitly say whether `data.values.<name>` is required when subcat-seeded values are present, or whether the seeded values alone are sufficient.

**The question:** When both forms are present, what is canonical? Options:

1. **`subcats.<name>.values` is authoritative.** The `data.values.<name>` bare-name list is deprecated — redundant information the subcat already carries.
2. **`data.values.<name>` is authoritative.** The subcat's `values` object is seed data only; attach-time resolution uses the bare-name list.
3. **Both must be present and agree.** Importers verify the two forms are consistent; disagreement is a validation error.

**Current canonical choice:** This bundle includes both — `data.values.<name>` as bare-name arrays AND `subcats.<name>.values` with enrichment — to match the existing watches sample. If the spec clarifies toward option 1, the `data.values` block can be removed.

**Why it matters:** Redundant data is a maintenance burden (two places to update a value name) and a possible source of disagreement bugs.

### CA-004 — Pexels API requires User-Agent header (note, not spec feedback)

**Severity:** tooling note

This is not feedback for the catdef spec; it is a note for future implementers who might write CATIO-producing tools that fetch photos from stock-photo APIs.

**Observed behavior:** The Pexels API (`api.pexels.com`) returns HTTP 403 Forbidden when a request omits the `User-Agent` header, even with a valid API key in `Authorization`. Adding any plausible `User-Agent` resolves the 403. The `fetch_photos.py` script in this directory sets `User-Agent: catdef-canonical-fetch/1.0 (+https://catdef.org)` and succeeds.

This is documented here so a future implementer of the reference or of any CATIO tool that optionally fetches stock photos can avoid the same diagnostic trail.

### CA-005 — Subcat `Logo` field empty for real-brand entry

**Severity:** editorial note

**What the canonical does:** The Maker subcat defines a `Logo` Photo field (to demonstrate the subcat-with-Photo capability). One of the Maker values — "Stanley Rule & Level Co." — is a real historical manufacturer. The canonical leaves its `Logo` empty.

**Why:** Using a generic stock image (e.g., a photo of some vintage tool) as a stand-in for a real company's trademark would be a misrepresentation. A better visual test of the Photo-in-subcat capability is provided elsewhere (the Location subcat's `Photo` field is populated with architectural imagery for Opera House and Van Bergen Schoolhouse).

**Question for the maintainer:** Is leaving a declared Photo field empty on a subcat value a conformance concern for health-score evaluation? The subcat field isn't marked `importance: "required"`, so the health score should accept it — but the canonical serves as a reference for what-is-acceptable patterns, and this particular choice should be sanctioned explicitly.

---

*This file is the author's log. Once `catdef.org/feedback` is a live endpoint, these items migrate to public, queryable feedback records.*
