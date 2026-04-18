# Proposal: Subcat value resolution — `subcats.<name>.values` is authoritative when present

**Status:** Draft
**Target version:** 1.4 (minor — introduces a new importer MUST, a new validation class, and a change to the required resolution order for Enumerated namespaces)
**Origin:** [canonical/AUTHORING_FEEDBACK.md CA-003](../canonical/AUTHORING_FEEDBACK.md) (first-implementor feedback during canonical authoring)
**Strategist decision:** [decisions/CA-003.md](../decisions/CA-003.md) — accept with modifications; this revision applies them.
**Conformance level affected:** All levels that support Enumerated fields — primarily L1 (Enumerated is L1-required) and L2+.

## Summary

Clarify the relationship between the two places a catdef can declare Enumerated-field values: the bare-name array at `data.values.<name>` and the enriched object at `subcats.<name>.values`. Today the spec defines both but is silent on which is authoritative when both appear, and silent on whether `data.values.<name>` is required when a subcat is declared. This proposal establishes: **when a subcat declares `values`, `subcats.<name>.values` is authoritative for that namespace; `data.values.<name>` becomes optional; if both appear, the `data.values.<name>` entries MUST be a subset of the subcat values' keys.** For Enumerated fields without a subcat, `data.values.<name>` remains the authoritative bare-name list.

## Motivation

The [`samples/watches.opencatalog`](../samples/watches.opencatalog) sample and the [canonical](../canonical/catalog.opencatalog) both declare Enumerated-field values in two places:

```json
{
  "subcats": {
    "Material": {
      "field_defs": [...],
      "values": {
        "Tin": {"Category": "Metal", ...},
        "Iron": {"Category": "Metal", ...}
      }
    }
  },
  "data": {
    "values": {
      "Material": ["Tin", "Iron"]
    }
  }
}
```

The names appear in both locations. The spec does not say:

- Whether both are *required* (and if so, whether mismatch is an error)
- Whether one is authoritative and the other is a convenience
- The import-time resolution order

A conformant importer has no defined behavior when the two disagree (e.g., `subcats.Material.values` contains "Tin" and "Iron"; `data.values.Material` contains "Tin" and "Bronze"). Different importers could legitimately pick: the union, the intersection, one side, or "first-wins." All four are defensible; none are specified.

During canonical authoring, the maintainer held both forms (mirroring the watches sample), without knowing whether the redundancy was:

1. Required by the spec
2. Forbidden by the spec (subtly — on the theory that one should be authoritative)
3. Tolerated by the spec (both work, one is redundant)

This proposal resolves the ambiguity with a single clear rule.

## Proposed change

### Amend CATDEF_SPEC.md §Subcats

Insert a new subsection after the Seed Values subsection, titled **Value resolution** (approximately line 580 of the current spec):

> ### Value resolution
>
> The Enumerated namespace `<target>` (e.g., "Brand", "Material", "Donor") can have its values declared in two places:
>
> 1. **`subcats.<target>.values`** — the enriched form: each value is an object with field data matching the subcat's `field_defs`.
> 2. **`data.values.<target>`** — the bare form: an array of value names only, without enrichment.
>
> When a subcat named `<target>` is declared:
>
> - `subcats.<target>.values` is **authoritative**. The set of value names in that object is the complete namespace.
> - `data.values.<target>` is **optional**.
> - A writer MAY omit `data.values.<target>` when `subcats.<target>.values` is declared; the `subcats.<target>.values` keys are the authoritative namespace. A writer MAY also include `data.values.<target>` as a subset — this is useful when the catdef is targeted at L1 runtimes that ignore subcats and benefit from a pre-declared namespace.
> - An importer encountering both MUST resolve from `subcats.<target>.values`.
>
> **Superset validation (mirror of forward-compat asymmetry).**
>
> A writer MUST NOT emit a catdef in which `data.values.<target>` contains names that are not keys of `subcats.<target>.values`. Writer-side validation tools MUST reject such documents.
>
> A reader encountering such a document MUST NOT reject it on this basis. The reader MAY warn that `data.values.<target>` contains names not seeded in `subcats.<target>.values`. The reader resolves the value namespace from `subcats.<target>.values` only; extra names in `data.values.<target>` are ignored.
>
> This asymmetry — writer strict, reader lenient — matches the pattern established by the `catdef` version-stamping rule.
>
> **Shared namespaces.** A subcat's value namespace is shared across all templates, fields, and subcats that reference it by target name. Multiple references resolve to the same value set; there is no per-reference scoping.
>
> When no subcat is declared for `<target>`:
>
> - `data.values.<target>` is the authoritative bare-name list. Used for Enumerated fields that don't need enrichment (simple option lists like "Mint / Excellent / Very Good / Good").
> - Declaring values via an un-seeded subcat (i.e., `subcats.<target>` exists with `field_defs` but no `values` object) is permitted; in that case `data.values.<target>` supplies the names and the `field_defs` apply once any enrichment is attached after import.
>
> The decision tree for a writer:
>
> ```
> If you want enriched values (e.g., Brand has Founded year, Country, Specialty):
>   → declare subcats.<target> with field_defs AND values
>   → data.values.<target> is optional; include it (as a subset) only
>     if you want pre-declared namespace visibility for L1 runtimes
>     that ignore subcats
>
> If you want bare-name values only (e.g., Condition is ["Mint", "Good", …]):
>   → declare data.values.<target> with a name array
>   → no subcats entry needed
>
> If you want a subcat to exist for future enrichment but have no seed data yet:
>   → declare subcats.<target> with field_defs only (no values)
>   → declare data.values.<target> with the name array
>   → each value will get empty subcat fields on import, fillable later
> ```

### Non-normative example rewrite

Add after the Value resolution subsection:

> **Example — preferred form for a catdef with a seeded subcat:**
>
> ```json
> {
>   "subcats": {
>     "Material": {
>       "field_defs": [
>         {"label": "Category", "type": "String", "sort_order": 10}
>       ],
>       "values": {
>         "Tin": {"Category": "Metal"},
>         "Iron": {"Category": "Metal"}
>       }
>     }
>   },
>   "data": {
>     "items": [...]
>   }
> }
> ```
>
> Note the absence of `data.values.Material` — it would be redundant with the keys of `subcats.Material.values`.

### Amend CATDEF_SPEC.md §Conformance Levels §Level 1

Append a paragraph clarifying the L1 runtime's Enumerated-namespace resolution:

> An L1 runtime that ignores subcats MUST be able to resolve an Enumerated field's value namespace from item references at render time when `data.values.<target>` is not present. The pre-declared namespace (from `subcats.<target>.values` or `data.values.<target>`) is an optimization; the item-reference fallback is the L1-mandatory path. This guarantees that a catdef using subcat-only Enumerated namespaces remains L1-renderable without requiring the L1 runtime to implement subcat resolution.

## Backward compatibility

**Existing catdefs:**

- The watches sample (`samples/watches.opencatalog`): currently declares `data.values` without subcats. Unchanged — the spec's new rules explicitly preserve the no-subcat case as bare-list authoritative.
- The canonical (`canonical/catalog.opencatalog`): currently declares BOTH `subcats.<name>.values` AND `data.values.<name>` with matching names. Under the new rules: valid (the `data.values` entries are a subset of subcat keys). The canonical deliberately retains both forms as a reference for the L1-friendly authoring pattern — `data.values.<target>` gives L1 runtimes that ignore subcats a pre-declared namespace without additional work.
- Any catdef in the wild that declares *both* with matching names: still valid.
- Any catdef that declares *both* with mismatched names (extra names in `data.values`): newly invalid. Migration: remove the extras, or add them to `subcats.<target>.values` with appropriate field data.

**Existing runtimes:**

- Importers that resolve from `data.values`: should be updated to resolve from `subcats.<target>.values` first when a subcat is declared. The resolved name set is the same when inputs match (common case today), so most existing importers render identically.
- Importers that resolve from subcats: no change.

**Migration utility:** a one-shot lint (non-normative) that checks every catdef file for the three validity cases:

1. Match (subcats-subset-of-data, or equal): valid; recommend simplification by removing redundant `data.values` entries.
2. Extra names in `data.values` beyond subcats keys: invalid; fix by either adding to subcats or removing from `data.values`.
3. No overlap problem: no change.

## Conformance tests

New fixtures in `conformance/fixtures/`:

- `valid_subcat_values_only.opencatalog` — declares `subcats.Brand.values` with two entries; no `data.values.Brand`. Items reference "Omega" and "Rolex" via Enumerated fields.
- `valid_subcat_plus_matching_data_values.opencatalog` — declares both forms with matching names (the legacy pattern). Valid but redundant.
- `valid_data_values_only.opencatalog` — declares `data.values.Condition` with `["Mint", "Good"]`; no subcat. Items reference Condition values.
- `invalid_data_values_superset.opencatalog` — declares `subcats.Brand.values` with `{"Omega": ...}` AND `data.values.Brand: ["Omega", "Rolex"]`. Invalid: `data.values` contains "Rolex" not present in subcat.
- `valid_empty_subcat_plus_data_values.opencatalog` — declares `subcats.Brand` with `field_defs` but no `values`, AND `data.values.Brand: ["Omega", "Rolex"]`. Valid: subcat defines the schema, data.values supplies names, enrichment attached later.

New tests in `conformance/test_subcat_values.py` (new file):

- **ft-subcat-values-01**: `valid_subcat_values_only.opencatalog` — importer resolves Item.Brand field values from `subcats.Brand.values` keys; items referencing "Omega" and "Rolex" resolve correctly.
- **ft-subcat-values-02**: `valid_subcat_plus_matching_data_values.opencatalog` — same resolution as ft-subcat-values-01; the redundant `data.values.Brand` entry does not produce different state.
- **ft-subcat-values-03**: `valid_data_values_only.opencatalog` — Enumerated field without subcat resolves values from `data.values.<target>`.
- **ft-subcat-values-04a (writer side)**: A writer-side validator MUST reject `invalid_data_values_superset.opencatalog`.
- **ft-subcat-values-04b (reader side)**: A reader MUST parse and render `invalid_data_values_superset.opencatalog` without refusal; it MAY emit a warning; the resolved namespace is the `subcats.<target>.values` keys only.
- **ft-subcat-values-05**: `valid_empty_subcat_plus_data_values.opencatalog` — value names come from `data.values`, subcat `field_defs` populate empty per-value fields.

## Alternatives considered

### A. `data.values.<name>` is authoritative; `subcats.<name>.values` is decorative seed data

Rejected. Forces every catdef with subcats to declare names twice forever — maintenance burden, staleness risk. Turns seed-value enrichment into a second-class feature. The current watches-sample pattern (both with matching names) is the artifact of a transitional design; the proposal's rule picks the endpoint.

### B. Keep both required; mismatch is always an error

Rejected. Too strict for nominal ergonomics. Writers need a reason to declare both; if there's no reason, demanding both is friction. The proposal allows redundancy (legacy pattern still works) but doesn't require it.

### C. Union semantics — take names from both sides

Rejected. Produces a silent bug class: a writer adds a name to `subcats.<target>.values` and forgets to update `data.values.<target>`; the name appears in the catalog but Enumerated fields referencing it via the data-side list don't know about the enrichment. Union semantics means "both sides contribute," which means mismatch is undetectable.

### D. `data.values.<name>` is the interop layer for non-subcat-supporting runtimes

Argument: L1 runtimes are allowed to ignore subcats per CATDEF_SPEC.md §Conformance Levels. If a catdef's Enumerated values are only in `subcats.<name>.values`, an L1 runtime gets an empty namespace. Therefore `data.values.<name>` must remain as the L1-accessible fallback.

Counter-rejected but nuanced: this is a real concern. The proposed rule's resolution: an L1 runtime that ignores subcats resolves Enumerated names from the items' field values themselves (at attach time) rather than from a pre-declared namespace. Items that reference "Omega" create an Omega value node on-the-fly. This is already the L1 fallback behavior for any Enumerated field whose value namespace isn't pre-declared. So the L1 case is covered by existing behavior, not by `data.values` redundancy.

**Adjustment noted:** the proposal's text should explicitly mention that L1 runtimes ignoring subcats can still use items as the value-name source. This is not a change to existing L1 conformance — it's a clarification that the `data.values` block is *not* required for L1-only rendering. Added to Open questions.

## Open questions

None remaining after CA-003 revisions. Prior open questions were resolved into normative text:

- L1-runtime guidance → promoted to §Conformance Levels §Level 1 amendment (item-inference is L1-mandatory).
- Validation strictness → resolved by the writer-strict / reader-lenient asymmetry in §Value resolution.
- Shared namespaces → resolved affirmatively in §Value resolution (shared by target name, no per-reference scoping).
- Round-trip normalization → declined (preserves importers that re-export byte-for-byte; ft-subcat-values-06 removed).

## Requested maintainer actions

- Sign off on `subcats.<target>.values` as authoritative-when-declared, with `data.values.<target>` as optional-subset.
- Sign off on the writer-strict / reader-lenient asymmetry for the superset case (mirror of the `catdef` version-stamping pattern).
- Sign off on adding the new `valid_*.opencatalog` and `invalid_*.opencatalog` fixtures, plus `test_subcat_values.py`.
- Approve the CATDEF_SPEC.md §Subcats edit and the §Conformance Levels §Level 1 item-inference amendment as drafted above (to be applied in a follow-on editorial PR once this proposal is accepted).
