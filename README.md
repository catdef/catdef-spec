# catdef

The open standard for **machine-enhanceable descriptors of real-world objects and catalogs**.

catdef defines two complementary concepts:

- **OpenThing** — a schema for describing any real-world object: its properties, measurements, classifications, provenance, and media.
- **OpenCatalog** — a schema for organizing collections of things: identity, branding, search, social features, and presentation.

A single `.opencatalog` file contains everything: the schema (templates, field definitions), the data (items, values), and the presentation (theme, settings). An AI that can see a photograph can write a catdef. A human with a spreadsheet can write a catdef.

## What's in this repo

| Path | Description |
|------|-------------|
| [CATDEF_SPEC.md](CATDEF_SPEC.md) | The catdef v1.4 specification — field types, subcats, views, inheritance, conformance levels, i18n, Policy Registry |
| [CATIO_SPEC.md](CATIO_SPEC.md) | The CATIO v1.4 bundled-transport specification — `.opencatalog` ZIP format (CATDEF + CATIO version in lockstep) |
| [samples/](samples/) | Sample catdef files you can open in any conformant renderer |
| [conformance/](conformance/) | The catdef Conformance Test Suite — 164 tests (plus 1 xfail tracking a known canonical drift) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to propose changes to the standard |
| [MCP_REFERENCE.md](MCP_REFERENCE.md) | Non-normative reference design for a Model Context Protocol server exposing catdef catalogs |
| [proposals/](proposals/) | In-flight proposals for spec changes (v1.4 and beyond) |
| [CLAUDE.md](CLAUDE.md) | Maintainer operating manual (AI-assisted review) — see CONTRIBUTING.md |

## File format

MIME types:
- `application/vnd.opencatalog+json` — a complete catalog (schema + data)
- `application/vnd.openthing+json` — a single classified object
- `application/vnd.catdef+json` — schema only (template definitions, no data)

```json
{
  "catdef": "1.4",
  "primaryLocale": "en",
  "product": { "name": "My Collection", "slug": "mycollection", ... },
  "inherits_from": "optional_model_slug",
  "views": { "primary_axis": "thing", "modes": ["grid"], "default": "grid" },
  "templates": [{ "name": "Item", "field_defs": [...] }],
  "subcats": { "Brand": { "field_defs": [...], "values": {...} } },
  "themes": { ... },
  "embed": { ... },
  "data": { "values": {...}, "items": [...] }
}
```

## Field types

13 field types covering the full spectrum of real-world object classification:

`String` `Integer` `Number` `RichText` `Enumerated` `Photo` `Table` `CloudFile` `URL` `Date` `Money` `Boolean` `GeoLocation`

Plus field-def attributes: `unique`, `default`, `format` (isbn, vin, sku, etc.), `unit`, `precision`, `min`/`max`, `circa`, `currency`, `range`, `scorable`, `primary`.

## v1.4 highlights

- **Polymorphic translatable fields** — any user-facing string field (`label`, `description`, `prompt`, `title`) may be authored either as a plain string or as an object with locale-keyed variants (`.en`, `.fr`, `.zh-Hant`, ...) plus author-declared policies. Monolingual catdefs stay trivial; multilingual catdefs are expressed without a parallel schema. RFC 4647 §3.4 Lookup governs locale fallback.
- **Policy Registry + value #9** — catdef is now a policy-bearing standard. The v1.4 closed vocabulary defines `.context` (translator disambiguator) and `.machine-translate` (`"Allow"` default; `"Never"` suppresses machine translation including OS-level browser features via `translate="no"`). Policy compliance is a first-class conformance dimension; runtimes that ignore a declared policy are non-conformant.
- **URL object schema** — `URL` fields formalize an object shape carrying `{url, title, description, og_image}` alongside the plain-string form. Link-preview cards, auto-extracted metadata.
- **Subcat value resolution rule** — when `subcats.<target>.values` is declared, it is authoritative for the Enumerated namespace. Writer-strict / reader-lenient superset validation mirrors the Postel's-Law pattern used across v1.4.
- **CATIO outer-archive convention** — ZIP-packaged catio bundles use the content-extension on the outer archive (`.opencatalog`, `.openthing`) rather than `.zip`, matching the `.docx` / `.jar` / `.epub` ecosystem convention. Content-sniffing is the authoritative discriminator; `.zip` is SHOULD-accepted for compatibility.
- **Writer-strict version stamping** — writers MUST stamp the minimum version that defines every feature used. A new non-normative Feature-Version Index maps every feature to its introducing version, making the rule mechanically enforceable.
- **CATDEF + CATIO lockstep versioning** — the co-equal core specs now pair versions (CATIO 1.4 pairs with CATDEF 1.4). Consumer specs (Theme Spec, MCP reference) continue to version independently.
- **Canonical reference file artifact** — a normative worked example (`canonical/riverside-heritage-reference-v1.4.opencatalog`) ships with the release; the new `ft-shape-07` conformance regression makes canonical-vs-validator drift structurally detectable.

## v1.3 highlights

- **Subcats** — enriched Enumerated values with their own field_defs. Stanley (the brand) has Founded/Country/Specialty/Logo. Artists have portraits. Venues have addresses.
- **Inheritance** — `inherits_from` enables partner/model catalogs. A watch-catalog platform publishes `watchomatic_model`; customers create catalogs that inherit schema, themes, and seed data.
- **Views** — `primary_axis` (thing/date/place) tells renderers the dominant organizing principle. A concert calendar declares `"primary_axis": "date"`, gets calendar-first rendering for free.
- **Range types** — `Number`/`Money`/`Date` with `range: true` for case diameter ranges, price ranges, exhibition dates.
- **Context-aware rendering** — `scorable` fields enable geo/time-weighted sorting. Same CATIO file renders differently on kiosks in different locations.
- **Embed declaration** — catalogs can be embedded in any website as iframes with declared defaults.
- **About page** — expanded `product` object (phone, website, address, hours, social, sections) turns every catalog into a proper web destination.

## Conformance levels

| Level | Name | Description |
|-------|------|-------------|
| L1 | Static | Browser-only, reads catdef files directly. No server. |
| L2 | Lightweight | API-backed with SQLite/D1. Read-write. |
| L3 | Full | Graph database. Full CRUD, audit log, photos. |
| L4 | Platform | Multi-tenant, auth, billing, social, AI onboarding. |

## Conformance test suite

Anyone can build a catdef renderer. To call it conformant, it must pass the test suite.

**The test suite is the standard.** See [conformance/](conformance/) for details.

## Feedback

File spec feedback at [catdef.org/feedback](https://catdef.org/feedback) — structured intake for AI agents and humans.

## License

MIT. See [LICENSE](LICENSE).

Build whatever you want. If it passes the tests, it's catdef.
