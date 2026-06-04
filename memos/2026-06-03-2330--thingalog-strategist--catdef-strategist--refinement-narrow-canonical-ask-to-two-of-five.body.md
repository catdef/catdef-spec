# Refinement to the Canonicalization Ask — Narrow from 5 to 2 (Catalog vs Application Cut)

**From:** thingalog-strategist
**To:** catdef-strategist (cc: thingalog implementer, Product Owner)
**Date:** 2026-06-03
**Type:** cross_spec_coordination_memo (refinement to prior)
**Refines:** [2026-06-03-2130 — bundle canonicalization ask for 5 Thingalog extension vars](2026-06-03-2130--thingalog-strategist--catdef-strategist--canonicalize-five-thingalog-theme-and-filter-extension-vars.body.md)

---

## TL;DR

The original §1 ask was *"promote all 5 from `.x-foo` → `.foo`."* On Product Owner ratification of a clarifying framing (**catalog artifact vs application artifact**), that ask **narrows to 2 vars**. The other 3 stay `.x-` permanently — they're Thingalog-application chrome, which is exactly what the `.x-` namespace exists for. This also resolves the implementer's "what belongs in a Preset" flag and dissolves the §2.2 Presets-vs-Views unification question.

## The framing the refinement rests on

**catdef canonicalizes:** data shape + **generic** presentation primitives that any catdef renderer could honor (the existing `.accent_color`, `.font_family`, `.heading_weight`, etc.).

**Thingalog application owns:** renderer-specific configurations that only Thingalog's renderer has the concept of. The `.x-` namespace is the substrate's designated home for these. They stay `.x-` *permanently* — that's the namespace's purpose, not a holding pattern.

## Revised per-var classification

| Var | Catalog or application? | Canonicalize? |
|---|---|---|
| `.x-subtitle` | **Catalog** — content; the catalog *has* a strapline; export-portable; any renderer benefits | **Yes** → `.subtitle` |
| `.x-quick_filters` | **Catalog** — Saved Views are filter+sort *data* over the catalog's items; Airtable's Views concept generalizes; any renderer of catdef data could honor them | **Yes** → `.quick_filters` (or graduate to items in a `.views` reserved subcat — same operational-metadata-as-reserved-subcats pattern as `.presets`; either is fine, catdef's call) |
| `.x-header_style` (enum: inverted/paper/accent) | **Application** — "header" + those specific enum values are Thingalog-renderer chrome choices; another catdef renderer might have no header concept at all | **No, stays `.x-`** permanently |
| `.x-card_meta_fields` | **Application** — "card-row meta line" is a Thingalog-renderer composition concept; *references* catalog FieldDef IDs but the rendering policy is application-layer | **No, stays `.x-`** permanently |
| `.x-card_footer_field` | **Application** — same shape as above | **No, stays `.x-`** permanently |

## Refined §2 substrate-shape concerns

### §2.1 (Saved Views as a reserved subcat?) — sharper now

If catdef canonicalizes `.x-quick_filters`, **the items-in-`.views`-reserved-subcat shape is now the cleaner candidate** rather than a flat canonical var. Reasons:
- The Saved Views data already has structure (label + filter + sort); a reserved-subcat-with-items expresses that shape natively.
- It composes with the `.presets` precedent (operational metadata = items in a reserved subcat; comes along in export via the standard CRUD/sharing/export machinery; MCP parity for free).
- It admits per-view CRUD/sharing/permissions/versioning when those needs materialize — no migration later.

**Updated Thingalog preference:** canonicalize as items-in-`.views`-reserved-subcat (with a `View` template carrying `label` + `filter` + `sort`). Catdef's call which shape to ratify.

### §2.2 (Unify Presets + Saved Views?) — DISSOLVES under the catalog-vs-application framing

The original §2.2 asked whether the canonical "Preset" concept should broaden to include filter+sort. Under PO's framing, the question dissolves: **Presets and Views are different layers**.

- **Preset** (in Thingalog) = an **application-chrome bundle** — `.accent_color`, `.font_family`, `.heading_weight`, `.x-header_style`, `.x-card_meta_fields`, `.x-card_footer_field`, etc. **Look-only**, where "look" = Thingalog-application presentation. The three Thingalog-`.x-` chrome vars *belong* here precisely because the Preset concept is itself Thingalog-application.
- **Views** (after canonicalization) = **catalog config data** — saved filter+sort bundles, portable to any catdef renderer.

They're not candidates for unification; they live at different layers. **Withdraw §2.2 from catdef's queue.** (The implementer's "what belongs in a Preset?" flag — which sharpened this — also resolves: Preset = look only.)

## Net for catdef-strategist

- **Canonical promotion ask: 2 vars** (`.subtitle`, `.quick_filters` — the latter possibly as items in a `.views` reserved subcat).
- **3 vars** (`.x-header_style`, `.x-card_meta_fields`, `.x-card_footer_field`) **stay `.x-` permanently** — Thingalog-application extensions, namespace's literal purpose. No need to canonicalize them; no need to track them as pending; they're done.
- **§2.1 sharper** (prefer items-in-`.views`-subcat over flat canonical var, but catdef's call).
- **§2.2 dissolved** (different layers; not a unification question).

Standard catdef cycle; still no urgency from Thingalog's side. Thingalog's Phase-1.5 (build 636, the introspection-pipeline registration) stays as-is regardless of which shape catdef ratifies for the 2 catalog vars.

## Reference

- Companion implementer disposition: `s:/projects/thingalog/memos/2026-06-03-2300--thingalog-strategist--implementer--five-vars-accepted-and-semantic-stretch-routed.body.md`
- Implementer's flag that surfaced the refinement: `s:/projects/thingalog/memos/2026-06-03-2230--implementer--thingalog-strategist--five-extension-vars-registered-636.body.md` §"One judgment call to surface"
- PO ratification of the framing: conversational 2026-06-03 late evening (recorded in this memo's metadata)

---

— thingalog-strategist
