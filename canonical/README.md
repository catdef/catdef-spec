# canonical

The canonical catdef reference bundle. A worked example that every implementer tests against, maintained in lockstep with the spec.

This directory is a normative spec artifact per the [MCP conformance levels proposal](../proposals/mcp-conformance-levels-and-reference.md). The bundle is what a catdef implementation — renderer, importer, CATIO-to-MCP server, conformance checker — points at to validate behavior against a single, stable, public example.

## What's in this directory

| File | Role |
|------|------|
| [`catalog.opencatalog`](catalog.opencatalog) | The CATIO JSON document (human-editable source). |
| `photos/` | 23 photos: 22 real photos sourced from Pexels and Unsplash, plus one generated placeholder (the Stanley logo). Referenced by filename from the JSON. |
| [`photos_manifest.json`](photos_manifest.json) | Per-photo provenance: provider, photographer, source URL, query used. |
| `riverside-heritage-reference-v1.4.opencatalog` | The packaged ZIP bundle — the actual canonical file implementers test against. Regenerated from `catalog.opencatalog` + `photos/` whenever either changes. |
| [`fetch_photos.py`](fetch_photos.py) | Reproducibility script. Rebuilds `photos/` from the query list. Reads `PEXELS_API_KEY` and `UNSPLASH_ACCESS_KEY` from the environment. No keys are stored in the repo. |
| `README.md` | This file. |

## Target spec version

**catdef 1.4-draft** — v1.3 is the current released spec, and this bundle deliberately exercises two draft-1.4 proposals:

- [MCP conformance levels and the CATIO-to-MCP reference](../proposals/mcp-conformance-levels-and-reference.md) — which establishes the canonical file as a spec artifact in the first place.
- [i18n via polymorphic translatable fields](../proposals/i18n-polymorphic-fields.md) — which introduces `primaryLocale`, polymorphic translatable-field objects, and the first two policies (`.context`, `.machine-translate`).

Both proposals are currently Draft. This canonical is the artifact that proves they are concretely implementable. When the proposals merge and v1.4 ships, the bundle version marker (`"catdef": "1.4"`) becomes non-provisional; until then, an L1 runtime reading this file should gracefully ignore the polymorphic-field object form and fall back to the primary-locale string (behavior defined in the i18n proposal's `ft-i18n-01`).

## What this bundle demonstrates

Exhaustively — at least one field, item, or subcat exercises each capability below.

### v1.3 capabilities

- **All 13 field types.** `String`, `Integer`, `Number`, `RichText`, `Enumerated` (single + multi), `Photo` (single + multi), `Table`, `CloudFile`, `URL`, `Date`, `Money`, `Boolean`, `GeoLocation`.
- **String formats.** `accession` on every Artifact (via `"format": "accession"`).
- **Number attributes.** `unit` (cm, g, mm), `precision`, `min`/`max`, `range` (`Case Diameter Range`).
- **Date attributes.** Exact dates, `circa: true`, `range: true` (`Exhibition Dates`, `Active Years`, `Operating Years`), `primary: true` (`Date Made`), `scorable: "recency"`.
- **Money attributes.** `currency: "USD"`, `range: true` (`Purchase Price Range`).
- **Integer attributes.** `scorable: "popularity"` (`Popularity`), bounded 0–100, `widget: "rating"`.
- **Enumerated attributes.** `multi`, `filterable`, `widget` overrides (`dropdown`, `checkbox_table`, `autocomplete`).
- **Photo attributes.** `multi: true`, `photo_labels`, `max_items`, plus the three transform modes:
  - `rotation` (items 1, 4, 10 — including a `rotation: 270` on item 10 and `rotation: 90` on item 4).
  - `crop_mode: "freeform"` (items 1, 3, 7 — with `crop_x1`/`y1`/`x2`/`y2`).
  - `crop_mode: "deskew"` (item 4 — the Van Bergen town plan — with all four corners declared).
- **Table with bbox.** `Inscriptions` table on items 1, 2, 8 uses `bbox` to spatially link table rows to photo regions (`photo_slot`, normalized `x`/`y`/`w`/`h`).
- **Subcats.** Five subcats (`ObjectType`, `Donor`, `Material`, `Region`, `Location`, `Maker`), each with multiple `field_defs` and seeded `values`. Includes:
  - Photo fields in subcats (`Location.Photo`, `Maker.Logo`).
  - An Enumerated-in-subcat **recursive** link (`Location.Region → Region`) — the mini-graph feature.
  - Subcat-namespace sharing: both the Artifact template and the Maker subcat reference the `Location` namespace.
- **`requires` declaration.** Every used feature and field type enumerated.
- **`hints`.** Realistic values for the corpus size.
- **`views`.** `primary_axis: "thing"`, four `modes`, `default_icon`, `kiosk_layout`, `mode_config` for both map and kiosk modes.
- **`themes`.** Named `riverside_vintage` theme — warm palette, serif heading font, light mode.
- **`embed`.** Fully populated block, `allowed_domains: ["*"]`, default view and size, `hide_sign_in: true`.
- **`settings`.** Every v1.3 setting exercised (`public`, `embed`, `social`, `inquire`, `export`, `health_score`, `history`, `trash`).
- **`product` / About page.** Extended `product` object with `sections`, social handles, address, hours, phone — the full About-page surface.
- **Context-aware rendering.** `scorable: "popularity"` (quilt — boosted on kiosk rotation) and `scorable: "recency"` (Date Made).

### v1.4 capabilities (i18n + policies)

- **`primaryLocale: "en"`** declared at the top level.
- **Polymorphic translatable fields.** Two items carry polymorphic `Title` values with `.en` + `.fr` variants:
  - Item 6 (field-recorded lullaby) — also carries `.context: "heritage-catalog"` to disambiguate for translators.
  - Item 11 (Cartwright wartime letter) — also carries `.machine-translate: "Never"`, demonstrating that the policy and human-curated translations coexist (the French variant is welcome; auto-translation is not).
- **Policies.**
  - **`.context: "heritage-catalog"`** on item 6's title — gives human translators the disambiguation context they need.
  - **`.machine-translate: "Never"`** applied across **nine** fields, demonstrating the safer-default pattern that the i18n decision recommends for narrative and culturally-specific content (per [decisions/i18n-polymorphic-fields.md](../decisions/i18n-polymorphic-fields.md) §Build directive item 1):
    - **Item-level provenance and titles:**
      - Item 2 `Provenance` (Cartwright pressed-flower album — historical family narrative with quoted donor phrasing).
      - Item 6 `Title` and `Provenance` (field-recorded lullaby — historical quotation; also `.fr` variant present).
      - Item 11 `Title` and `Provenance` (WWI letter — quoted donor phrasing "Jim never came home"; also `.fr` variant present).
    - **Subcat narrative fields:**
      - Donor `Notes` for Helen Cartwright (multi-gift donor narrative; touches items 2, 8, 11).
      - Donor `Notes` for Hiram Davies (multi-generational family narrative; touches items 3, 10).
      - Location `Notes` for Riverside Millworks (family-business narrative; touches items 1, 3).
      - Location `Notes` for Van Bergen Schoolhouse (one-room-school history; touches items 4, 6).

The `.machine-translate: "Never"` default is `"Allow"` per the spec — authors of culturally-specific content must opt in. The canonical demonstrates the pattern so authors copying it inherit the safer default for content where ML translation does harm (paraphrasing historical quotations, mistranslating named entities, fabricating locale variants of personal narratives).

A conformant implementation MUST NOT machine-translate any of the `.machine-translate: "Never"` fields regardless of viewer locale, per value #9 (policy compliance as a conformance requirement). This is tested by `ft-i18n-08` and `ft-i18n-09` in `conformance/policies/test_i18n_policies.py`.

## What this bundle does not demonstrate

By design:

- **`inherits_from`.** A canonical file must stand alone; it has no parent catdef to inherit from. A separate fixture will demonstrate partner inheritance when the reference implementation supports it.
- **Write operations (`create_item`, `update_field`, etc.).** M1 conformance is read-only. M2 canonical content will be added when M2 is specified.
- **Kiosk rendering over time.** The `scorable` fields are declared but their runtime behavior depends on environmental signals (viewer geolocation, local time) that a static file cannot exercise.

If your renderer passes this bundle but fails on any of those cases, it is testing a different conformance dimension.

## The fictional corpus

The **Riverside Heritage Society** is not a real institution. Every item, donor, maker, and location in the catalog is invented, with the following carefully-scoped exception:

- **Stanley Rule & Level Co.** is a real historical manufacturer (founded 1857, New Britain, Connecticut; acquired by Stanley Works in 1920). It is referenced in its historical form to ground the canonical in a recognizable example and echo [CATDEF_SPEC.md's Stanley subcat example](../CATDEF_SPEC.md). The Bailey-pattern plane (item 3) is described consistent with the historical record. The Maker subcat's `Logo` Photo field points to a **generated placeholder image** (`maker_stanley_logo.jpg`) — a simple typeset "STANLEY / RULE & LEVEL CO. / NEW BRITAIN, CONN. / EST. 1857" on the bundle's theme background, with the word "PLACEHOLDER" printed at the bottom so no one mistakes it for an authentic Stanley trademark. This lets the Logo field exercise the subcat-Photo feature on a real-brand entry without misrepresenting a trademark.

**The fictional corpus choice was deliberate:**

- A real-collection-based canonical (the original proposal named the Welch Arctic Collection — a private archive held by the catdef maintainer) would raise consent questions for every human named, especially where cultural sensitivity applies. Better to ship a smaller, fully-cleared canonical than one with consent questions.
- A synthetic local-history museum spans enough object types, materials, and provenance patterns to exercise the full spec surface without impersonating any real institution or person.
- Future canonicals may cover other domains (field biology, concert calendars, retail catalogs) as separate bundles, each exercising features that benefit from a different corpus shape.

### Photos are representative, not depictive

Each item references one or more photos from Pexels or Unsplash. **The photos do not depict the described items, donors, or places** — they are visually-suitable imagery in the same genre. Example: the "Cartwright family pressed-flower album" is described as having been kept by Anna Cartwright from 1887 to 1894; the photo of its cover is a real antique leather book, but not Anna's book. The photo of a carpenter's plane is a real Bailey-pattern plane, but not the one Ellis Davies owned.

This distinction matters because the canonical is inspected by humans reading real metadata. Anyone referencing "Helen Cartwright" or "Riverside Opera House" in downstream documentation is referencing fictional entities invented for this file. The photos are included to exercise CATIO's photo-bundle transport (filename resolution inside the ZIP, per-item photo-transform edges, crop and deskew mechanics, bbox spatial-linking) — not to document actual historical objects.

## Using this bundle as a fixture

### As a renderer test input

Open `riverside-heritage-reference-v1.4.opencatalog` as you would any `.opencatalog` file. A compliant renderer produces:

- A grid of 12 items with photos, titles, and short metadata summaries.
- Per-item detail views exercising Tables (with bbox-to-photo hover linking), RichText rendering, Date/Money/Number formatting, GeoLocation pinning.
- A Sub-Catalogs view listing the five subcats and their seeded values, including photos for Locations.
- About page with the three declared sections.
- A kiosk mode that rotates items with the quilt (highest popularity) weighted highest.

### As an MCP server input

Point a CATIO-to-MCP server at the ZIP. The seven M1 conformance tests in the [MCP proposal](../proposals/mcp-conformance-levels-and-reference.md#conformance-tests) all run against this bundle.

### As a policy-compliance test

Run any translation tool that reads catdef against this bundle. For every `.machine-translate: "Never"` field, confirm that no new locale variant was added. Failure is non-conformance per value #9.

## Reproducing the photos

The photo files are committed to the repo for determinism — every implementer sees the same bytes. To re-fetch (e.g., after a photo is removed from its provider):

```bash
PEXELS_API_KEY=... UNSPLASH_ACCESS_KEY=... python fetch_photos.py
```

The script is idempotent: already-cached filenames are skipped. To force a re-fetch, delete the file from `photos/` and remove its entry from `photos_manifest.json`, then re-run.

## Packaging the ZIP

The ZIP bundle is built from the JSON + `photos/` with a simple zip command:

```bash
cd canonical
zip riverside-heritage-reference-v1.4.opencatalog catalog.opencatalog photos/*.jpg
```

The bundle's inner JSON document is `catalog.opencatalog` at the root, and photos live in `photos/` per [CATIO_SPEC.md §Structure](../CATIO_SPEC.md).

## Credit and license

### Catalog content

All JSON content — item descriptions, fictional donors, invented provenance narratives, schema and subcat field definitions — is authored by **catdef-maintainer** (the AI-maintainer role defined in [CLAUDE.md](../CLAUDE.md)) on behalf of the catdef project and licensed under **MIT**, consistent with the rest of the spec repository. See [LICENSE](../LICENSE).

The canonical file is a spec artifact. Implementers may freely use, reproduce, and redistribute it as part of testing against the catdef spec. Modifications should be filed as feedback to `catdef.org/feedback` rather than forked silently, so the canonical stays aligned with the spec.

### Photos — separate licensing

Each photo carries its own license from its provider. These licenses **are not MIT** and are not altered by this bundle's license. The photos are included under Pexels and Unsplash terms, both of which permit free use (including commercial) with attribution appreciated but not legally required. Neither provider permits redistribution of the photos as standalone stock imagery — but embedding them in a specification's worked example, as here, is within both licenses' permitted uses.

**Pexels License:** https://www.pexels.com/license/
**Unsplash License:** https://unsplash.com/license

### Per-photo attribution

Full attribution table. Each row lists the filename, the provider, the photographer (linked to their profile), and a link to the photo's page on the provider's site.

| File | Provider | Photographer | Source |
|------|----------|-------------|--------|
| `item01_tin_locomotive_front.jpg` | Pexels | [Milada Vigerova](https://www.pexels.com/@milivigerova) | [view](https://www.pexels.com/photo/collection-of-vintage-toys-on-shelf-5984873/) |
| `item01_tin_locomotive_mark.jpg` | Pexels | [BOOM Photography](https://www.pexels.com/@boom) | [view](https://www.pexels.com/photo/small-wind-up-toy-bus-12585769/) |
| `item01_tin_locomotive_side.jpg` | Unsplash | [Ray Harrington](https://unsplash.com/@raymondo600) | [view](https://unsplash.com/photos/black-and-red-train-toy-izhZFfh9JfE) |
| `item02_flower_album_cover.jpg` | Unsplash | [Pierre Bamin](https://unsplash.com/@bamin) | [view](https://unsplash.com/photos/two-hard-bound-books-oH9JzD28T-Y) |
| `item02_flower_album_page.jpg` | Pexels | [Andreea Ch](https://www.pexels.com/@andreea-ch-371539) | [view](https://www.pexels.com/photo/dried-flowers-1261182/) |
| `item03_plane_mark.jpg` | Unsplash | [Judy Beth Morris](https://unsplash.com/@judy_beth_morris_idaho) | [view](https://unsplash.com/photos/a-close-up-of-a-pen-on-a-table-rbvAciTatfM) |
| `item03_plane_overview.jpg` | Pexels | [Dan Lynch](https://www.pexels.com/@dan-lynch-2153544483) | [view](https://www.pexels.com/photo/vintage-wood-plane-in-a-traditional-woodshop-36678066/) |
| `item04_map_scan.jpg` | Pexels | [Aaditya Arora](https://www.pexels.com/@aaditya-arora-188236) | [view](https://www.pexels.com/photo/world-map-illustration-592753/) |
| `item05_phone_base.jpg` | Unsplash | [Andrey Soldatov](https://unsplash.com/@andrilliardbond) | [view](https://unsplash.com/photos/a-black-and-white-photo-of-a-remote-control-3glpDr9aPiw) |
| `item05_phone_front.jpg` | Pexels | [幻影 多媒体](https://www.pexels.com/@1849646) | [view](https://www.pexels.com/photo/green-telephone-3435213/) |
| `item05_phone_handset.jpg` | Pexels | [Ann H](https://www.pexels.com/@ann-h-45017) | [view](https://www.pexels.com/photo/purple-telephone-on-blue-background-10791679/) |
| `item06_lullaby_sheet.jpg` | Pexels | [Ylanite Koppens](https://www.pexels.com/@nietjuhart) | [view](https://www.pexels.com/photo/music-notes-934067/) |
| `item07_milk_bottle.jpg` | Pexels | [Suzy Hazelwood](https://www.pexels.com/@suzyhazelwood) | [view](https://www.pexels.com/photo/grayscale-photo-of-bottles-in-groups-with-milk-4578396/) |
| `item08_quilt_detail.jpg` | Unsplash | [Hans-Peter Traunig](https://unsplash.com/@hanspetertraunig) | [view](https://unsplash.com/photos/abstract-textured-fabric-with-purple-and-pink-splashes-xRfFUQABAMI) |
| `item08_quilt_overview.jpg` | Pexels | [Erik Mclean](https://www.pexels.com/@introspectivedsgn) | [view](https://www.pexels.com/photo/handmade-patchwork-quilt-8266834/) |
| `item09_campaign_button.jpg` | Pexels | [Berna](https://www.pexels.com/@mibernaa) | [view](https://www.pexels.com/photo/collection-of-vintage-enamel-pins-in-suitcase-33305426/) |
| `item10_ice_pick.jpg` | Pexels | [César Guillotel](https://www.pexels.com/@cesar) | [view](https://www.pexels.com/photo/an-axe-in-stamp-in-a-tree-stump-12665253/) |
| `item11_letter.jpg` | Pexels | [Pixabay](https://www.pexels.com/@pixabay) | [view](https://www.pexels.com/photo/white-ruled-paper-99562/) |
| `item12_playbill_back.jpg` | Unsplash | [Aryasatya Rafa Prayitno](https://unsplash.com/@911mind) | [view](https://unsplash.com/photos/wrinkled-paper-with-brown-stains-and-creases-OdDW-0Dy91Y) |
| `item12_playbill_front.jpg` | Pexels | [lil artsy](https://www.pexels.com/@lilartsy) | [view](https://www.pexels.com/photo/assorted-color-butterflies-wall-decor-1793030/) |
| `loc_opera_house.jpg` | Pexels | [Brady Wilson](https://www.pexels.com/@bradymwilson) | [view](https://www.pexels.com/photo/facade-of-the-ludlow-theater-ludlow-kentucky-15238044/) |
| `loc_van_bergen_schoolhouse.jpg` | Pexels | [Gene Samit](https://www.pexels.com/@gene-samit-546626702) | [view](https://www.pexels.com/photo/historic-red-and-white-schoolhouse-in-pennsylvania-36844158/) |
| `maker_stanley_logo.jpg` | Generated placeholder | catdef-maintainer | Generated by [`fetch_photos.py`](fetch_photos.py) — clearly labelled "PLACEHOLDER" |

The authoritative, machine-readable source is [`photos_manifest.json`](photos_manifest.json) — it carries every field above plus the search query used, for reproducibility.

## Notes from the author (first-implementor feedback)

Building this canonical flushed out a handful of spec-prose questions. Per [CLAUDE.md](../CLAUDE.md)'s "every implementation files feedback like any other consumer" rule, the catdef-maintainer role does not fix these editorially in the flow of canonical authorship — it logs them as reports. The full log is in [AUTHORING_FEEDBACK.md](AUTHORING_FEEDBACK.md) in this directory.

Summary of items raised, with triage state:

| CA | Topic | Disposition |
|-----|------|-------------|
| CA-001 | Outer archive extension for ZIP-bundled CATIO | **Accept w/ mods** — [decisions/CA-001.md](../decisions/CA-001.md) · [proposal](../proposals/catio-bundle-extension.md) · target v1.4 · canonical compliant |
| CA-002 | `primaryLocale` / version-stamp semantics | **Accept w/ mods** — [decisions/CA-002.md](../decisions/CA-002.md) · [proposal](../proposals/version-stamp-semantics.md) · target v1.4 · canonical sanctioned under reference-document exception |
| CA-003 | `data.values` vs `subcats.<name>.values` authority | **Accept w/ mods** — [decisions/CA-003.md](../decisions/CA-003.md) · [proposal](../proposals/subcat-value-resolution.md) · target v1.4 · canonical compliant (permissive MAY-include pattern) |
| CA-004 | Pexels API requires `User-Agent` | Tooling note — not spec feedback |
| CA-005 | Subcat Photo field empty for real-brand entry | Resolved by implementation ([PR #14](https://github.com/catdef/catdef-spec/pull/14) — Stanley placeholder image) |
| CA-006 | Conformance validator gaps vs. v1.3 value shapes (+ v1.4-draft polymorphic) | Pending triage — proposal drafting in progress |

All three spec-bearing items (CA-001, CA-002, CA-003) have been triaged and target v1.4. Spec-text edits are held under the strategist's v1.4 release-management constraint until the full bundle is coherent — these three plus the i18n / `primaryLocale` proposal and the MCP conformance work land together or not at all. This canonical is already compliant with the three revised proposals as written; no content changes are needed when the spec-text eventually lands. The report format in AUTHORING_FEEDBACK.md will migrate to `catdef.org/feedback` once that endpoint is live; until then the file serves as the audit trail.

---

*Canonical file version: 1.4-draft, first edition. April 2026.*
