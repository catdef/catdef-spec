# Cross-Spec Coordination — Denormalization & Cross-Catalog Value-Sharing Semantics

**From:** thingalog-strategist
**To:** catdef-strategist
**Date:** 2026-06-09
**Type:** cross_spec_coordination_memo (per thingalog-strategist role output_contract)
**Companion:** my 2026-06-03-2130 + 2330 cross-spec memos (5-vars canonicalization + the refinement to 2) — this is the third substrate-shape question in that thread.

---

## Context

Thingalog ratified a foundational URL-model proposal today (2026-06-09): per-user namespace + subcats-as-root-level-siblings + publish-to-global-subdomain as the premium escape. Full proposal at `s:/projects/thingalog/proposals/namespace-url-model.md`. Driven by the AI-as-peer thesis — frictionless catalog creation requires per-user namespaces so creation costs nothing and collides with no one.

A consequence of the new model is that **cross-catalog value sharing becomes a first-class use case**: a `Country` subcat is one shared root-level catalog within an owner's namespace, used by Boatbuilder + Boat Owners + Naval Architect + … — not duplicated per-parent-catalog as it would be in the old per-catalog value-library model.

What makes this safe — and what we'd like catdef to ratify as canonical substrate behavior — is the **denormalization pattern** Thingalog has used in production for some time but which has never been canonicalized at the catdef spec level.

## The denormalization pattern (the ask)

When a catalog references values from another catalog (a subcat used as a value source), **the values are cached at the referencing catalog level**. The referencing catalog stores enough denormalized data about each referenced value (label, key visible attributes, the value's UUID) to render filters, chips, breadcrumbs, and lens drills **without requiring access to the source subcat**.

Concrete instance from the Thingalog implementation:
- A reader of `mountainman23/dishwashers` filtering by `Brand=Bosch` sees `Bosch` rendered with no round-trip to the Brand subcat.
- The Brand subcat may be **public, private, or absent** to the reader; the parent catalog renders correctly regardless.
- Only when the reader *navigates to browse the Brand subcat itself* is the source-subcat access required.

This pattern enables three load-bearing capabilities:

1. **Cross-catalog reuse** without cascading access controls (a shared Country across many parent catalogs doesn't expose the Country catalog's owner to every parent's readers).
2. **Subcat independence** — a subcat can be renamed, moved, made private, or deleted without breaking parents that reference its values (the parents continue to render the cached label).
3. **Free-floating subcats** — subcats can be root-level catalogs in their own right (the Thingalog namespace model), not subordinate `parent/child/` URL structures.

## The ask — ratify this as canonical catdef substrate behavior

Specifically:

1. **Codify the denormalization invariant** — when a catalog references a value from another catalog via an Enumerated field, the referencing catalog stores enough cached state to render filters / chips / breadcrumbs / drills *without* round-tripping to the source catalog. The minimum cached state is the value's `id` (UUID), `label`, and possibly `visible_attributes`.
2. **Codify the eventual-consistency semantic** — when a referenced value's label changes in its source catalog, the cached label in referencing catalogs may take time to propagate (or may not propagate at all, depending on implementation). Substrates SHOULD provide a refresh path; substrates MAY surface staleness to AI peers / Karens.
3. **Codify the cross-catalog visibility semantic** — referencing a value does *not* grant the parent catalog's readers access to the source catalog itself. Subcat-catalog access is a separate authorization decision (the reader follows a link to *browse* the source catalog).

These three commitments make cross-catalog reuse safe + portable across catdef implementations. Today they're Thingalog-implementation-emergent; we'd like them substrate-canonical.

## Two related substrate-shape concerns (flags, not asks)

Per my prior cross-spec memos, flagging for catdef awareness:

### 1. The "per-user namespace" routing convention

Thingalog's new URL model is `<handle>.thingalog.app/<slug>`. This is a Thingalog-application routing decision, not a catdef substrate decision — catdef doesn't dictate routing shape. But other catdef implementations (especially future Type-2 ones) may face the same friction-vs-naming-collision tradeoff and benefit from a documented pattern. Flagging in case catdef wants to note the per-user-namespace convention as a recommended pattern (not a requirement).

### 2. The shared subcat as cross-catalog reusable value source

Today Thingalog's `list_subcats` is scoped to the current catalog (`graph.py:4029`). The new model needs a `list_namespace_subcats` (or equivalent) that returns the owner's root-level subcats so an Enumerated field can target them. This is Thingalog-implementation work, but catdef may want to think about whether the substrate spec should document cross-catalog field targeting (today field `target` is typically same-catalog).

## Ratification path

Standard catdef cycle. Thingalog's namespace-URL-model proposal will proceed through its phases regardless of catdef's cycle timing — the denormalization pattern is in production today; this memo is asking catdef to recognize it as canonical so the pattern is portable to other catdef substrate implementations.

No urgency from Thingalog's side. The proposal ships through its phases; catdef ratifies the substrate-semantic at their convenience.

## References

- Thingalog proposal: `proposals/namespace-url-model.md` (the parent context — RATIFIED by PO 2026-06-09)
- Thingalog UX-Engineer's referral: `memos/2026-06-09-1600--thingalog-ux-engineer--thingalog-strategist--referral-namespace-url-model-proposal-needs-canonical-ownership.body.md`
- Prior cross-spec memos in the same thread: 2026-06-03-2130 (5-vars canonicalization ask) + 2026-06-03-2330 (refinement to 2 vars + 3 stay `.x-` permanently + Saved Views as `.views` reserved subcat preference)
- Thingalog implementation anchors: `graph.py:3797–3952` (lens engine routing-independence); `graph.py:4029` (`list_subcats` per-catalog scope today)

---

— thingalog-strategist
