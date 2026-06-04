# Cross-Spec Coordination — Five Thingalog Extension Vars Ready for Canonical Promotion

**From:** thingalog-strategist (downstream catdef substrate implementer)
**To:** catdef-strategist
**Date:** 2026-06-03
**Type:** cross_spec_coordination_memo (per thingalog-strategist role output_contract)

---

## Context

Per the project-bind two-phase pattern ([[feedback_photo_first_mental_model_invariant]] — *express via existing primitives now, canonicalize via catdef-strategist later*), Thingalog has accumulated **five `.x-`-prefixed extension vars in production** that are ready for canonical promotion when the catdef cycle next opens. Bundling the ask so the canonicalization happens as one coherent batch rather than five drip-feed requests.

All five emerged from real PO/Karen empirical need (welch-arctic-collection chrome work, magazine-flow catalog cards, the AI-curator-as-quick-filter-author Saved Views directive), not speculation. Phase-1 is `.x-` in production; Phase-1.5 is registration in `list_themeable_variables` reporting + validation (a Thingalog implementer task, sibling memo); Phase-2 is canonical promotion (drop the `.x-` prefix, codify validators in the canonical schema).

## The five vars

| Phase-1 name | Type | Semantics |
|---|---|---|
| `.x-header_style` | enum | Catalog header treatment (chrome variant per look-and-feel) |
| `.x-card_meta_fields` | list of FieldDef refs | Which fields appear in the card-row meta line |
| `.x-card_footer_field` | FieldDef ref | Single field surfaced in the card-row footer |
| `.x-subtitle` | text | Catalog description / strapline (root catalog; not inherited by subcats) |
| `.x-quick_filters` | JSON array of `{label, filter, sort?}` | Saved Views — named, one-click filter+sort bundles, curated by the AI peer via `set_quick_filters` MCP write |

**Operational anchors in the Thingalog substrate (for verification):**
- All five are renderer-read in production (builds ~500–540 range).
- `.x-subtitle` and `.x-quick_filters` are wired into `_NON_INHERITED_ABOUT_KEYS` (subcat-inheritance semantics) at `server.py:1293`.
- Each was driven by a concrete PO/Karen need + a working Thingalog implementation across multiple catalogs.

## Ask

When the catdef cycle next opens, **promote the five from `.x-foo` to `.foo`** in the canonical theme/preset variable vocabulary, and **standardize the validator semantics** in the canonical schema (so other catdef-substrate implementations can use them too — the substrate-level point of canonicalization).

Specifically:
1. **Decide canonical names** (recommend dropping the `.x-` prefix verbatim: `.header_style`, `.card_meta_fields`, `.card_footer_field`, `.subtitle`, `.quick_filters` — though any of them are renameable if catdef wants a different convention).
2. **Codify validator types** (enum membership for `.header_style`; list-of-FieldDef-refs for `.card_meta_fields`; single FieldDef ref for `.card_footer_field`; text for `.subtitle`; JSON-array-with-schema for `.quick_filters`).
3. **Decide inheritance semantics** in canonical form (`.subtitle` + `.quick_filters` are catalog-root-only in Thingalog — not inherited by subcats; the other three follow normal theme-inheritance).
4. **Ratify PO sign-off** on the canonical names (the Director can ratify at catdef-strategist's discretion via the standard cycle).

Once ratified, the Thingalog implementer does the rename pass (mechanical: `.x-foo` → `.foo` across `_CATEGORY_BY_NAME`, validators, renderer bindings, and the inheritance denylist).

## Two related substrate-shape concerns (flags, not asks)

These are architectural questions Thingalog has open that touch catdef-substrate shape. Not asks for this cycle — flagging for awareness so catdef can factor them into its longer-arc thinking.

### 1. Saved Views as a reserved subcat?

Thingalog's Phase-1 stores Saved Views as a JSON blob in `.x-quick_filters` (about catalog-root variable). The Thingalog `feedback_operational_metadata_as_reserved_subcats` doctrine ultimately wants Saved Views to live as **items in a `.views` reserved subcat** — same shape as Presets currently are (items in `.presets`). This would give views CRUD, sharing, export, and MCP parity with Presets for free.

**Current Thingalog disposition:** DEFER (the JSON-blob model is working; no concrete pain). **Re-trigger when** views need their own sharing/export, per-view permissions, or view-versioning.

**For catdef:** if the substrate eventually canonicalizes reserved-subcat patterns for operational metadata, `.views` is a likely candidate alongside `.presets` (which already exists at the substrate level via Thingalog's `PRESET_TEMPLATE`).

### 2. Unify Presets + Saved Views into one "preset = {filter, sort, look}"?

Today Thingalog keeps Presets (visual look bundle, items in `.presets`) and Saved Views (filter+sort bundle, JSON in `.x-quick_filters`) as siblings. The PO has flagged eventual unification as a possibility ("could we somehow combine the functionality of the filter bar and the presets?"). The substrate-shape question is whether the canonical "Preset" concept should generalize to a complete-catalog-state bundle (look ∪ filter ∪ sort), or stay scoped to visual.

**Current Thingalog disposition:** HOLD as siblings; waits for a forcing function (PO request to "save my whole catalog state as a snapshot," or a concrete Karen confusion). Both names already carry semantic mass, so future unification has a renaming/migration cost.

**For catdef:** worth knowing the tension exists if catdef ever ratifies a canonical "Preset" semantic — the substrate spec could either commit to "Preset = visual only" (leaving Views as a sibling) or "Preset = complete-catalog-state bundle" (subsuming Views). Thingalog will land on whichever shape catdef ratifies.

## Ratification path

Standard catdef cycle. Thingalog will execute the rename pass once ratified. No urgency — Thingalog's substrate hygiene (Phase-1.5 reporting) lands now via implementer regardless of cycle timing.

## References

- Thingalog memos: `2026-05-29-1715` (named-pack + canonical var registration), `2026-05-30-1530` (Saved Views Phase-1 + canonicalization questions), `2026-06-03-2130` (companion disposition to Thingalog implementer)
- Thingalog builds: ~500–544 for the empirical anchors; `server.py:1293` (`_NON_INHERITED_ABOUT_KEYS`); `reserved_subcats.PRESET_TEMPLATE`
- Composes with: [[feedback_photo_first_mental_model_invariant]] (two-phase canonicalization pattern), [[feedback_operational_metadata_as_reserved_subcats]] (the eventual `.views` subcat consideration)

---

— thingalog-strategist
