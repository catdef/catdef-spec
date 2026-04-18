# Proposal: Subcat value resolution — `subcats.<name>.values` is authoritative when present

**Status:** Draft
**Target version:** 1.3.1 (patch — clarifies ambiguous prose; the watches sample and the canonical currently exhibit the redundancy)
**Origin:** [canonical/AUTHORING_FEEDBACK.md CA-003](../canonical/AUTHORING_FEEDBACK.md) (first-implementor feedback during canonical authoring)
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
> - `data.values.<target>` is **optional**. If present, its entries MUST be a subset of the keys of `subcats.<target>.values`. Extra names in `data.values.<target>` that do not appear in `subcats.<target>.values` are a validation error.
> - A writer SHOULD omit `data.values.<target>` when `subcats.<target>.values` is declared, to avoid redundancy.
> - An importer encountering both MUST resolve from `subcats.<target>.values` and MAY validate that `data.values.<target>` (if present) is a subset.
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
>   → omit data.values.<target> (subcats.values keys ARE the namespace)
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

## Backward compatibility

**Existing catdefs:**

- The watches sample (`samples/watches.opencatalog`): currently declares `data.values` without subcats. Unchanged — the spec's new rules explicitly preserve the no-subcat case as bare-list authoritative.
- The canonical (`canonical/catalog.opencatalog`): currently declares BOTH `subcats.<name>.values` AND `data.values.<name>` with matching names. Under the new rules: still valid (the `data.values` entries are a subset of subcat keys), but the `data.values` block is redundant and SHOULD be removed. A follow-on canonical PR will do this cleanup.
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
- **ft-subcat-values-04**: `invalid_data_values_superset.opencatalog` — importer rejects or warns; a non-conformant importer silently drops "Rolex"; a conformant importer raises a validation error.
- **ft-subcat-values-05**: `valid_empty_subcat_plus_data_values.opencatalog` — value names come from `data.values`, subcat `field_defs` populate empty per-value fields.
- **ft-subcat-values-06**: Round-trip export — an importer that reads `valid_subcat_plus_matching_data_values.opencatalog` and re-exports SHOULD omit the redundant `data.values.<target>` block on the re-export.

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

1. **L1-runtime guidance.** An L1 runtime encountering a catdef where Enumerated values are only in `subcats.<target>.values`: the runtime ignores subcats (allowed) and therefore sees no pre-declared namespace. Does it infer values from item references, or fail? Recommendation: infer from items, per existing behavior when `data.values` is omitted for un-subcat'd Enumerated fields. Add explicit guidance to CATDEF_SPEC.md §Conformance Levels §Level 1.

2. **Validation strictness.** When `data.values.<target>` has names not in `subcats.<target>.values` (the "superset" case): reject outright, or warn-and-merge? Recommendation: reject outright at write time (writer-side validation); warn-and-merge at read time (reader-side leniency, mirroring CA-002's asymmetry). But this is more complex than the current draft; simplify to "validation error at import" and let writers decide what to do with the error.

3. **Seed-value attribution for shared namespaces.** The canonical's `Location` subcat is referenced by both the Artifact template's `Origin` field AND the Maker subcat's `Workshop Location` field. Both use the same Location values. Under the new rule, `subcats.Location.values` is authoritative. Confirm no ambiguity arises when multiple subcats / templates share a target namespace. *(The canonical works today with this pattern; expected answer: no change needed.)*

4. **Round-trip normalization.** Should round-trip (read → export) automatically strip redundant `data.values` entries? This is a should-it-happen (behavioral) and a would-it-break-anyone (interop risk) question. Recommendation: ft-subcat-values-06 makes this a SHOULD for conformant importers; writers that preserve legacy input remain permitted.

## Requested maintainer actions

- Sign off on `subcats.<target>.values` as authoritative-when-declared, with `data.values.<target>` as optional-subset.
- Confirm the validation-error disposition for the superset case (vs. merge-with-warning).
- Sign off on adding the new `valid_*.opencatalog` and `invalid_*.opencatalog` fixtures, plus `test_subcat_values.py`.
- Approve the CATDEF_SPEC.md §Subcats edit as drafted above (to be applied in a follow-on editorial PR once this proposal is accepted).
- Acknowledge the follow-on canonical simplification — after this proposal lands, a small PR drops the redundant `data.values.<name>` entries from `canonical/catalog.opencatalog` for names already seeded in `subcats.<name>.values`.
