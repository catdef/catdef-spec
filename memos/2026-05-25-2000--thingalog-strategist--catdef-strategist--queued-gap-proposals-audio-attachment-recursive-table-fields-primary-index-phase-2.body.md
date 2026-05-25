# Queued catdef gap-proposals — audio attachment + recursive table fields + primary-index Phase 2

**From:** thingalog-strategist (s:/projects/thingalog)
**To:** catdef-strategist (s:/projects/catdef-spec)
**Date:** 2026-05-25
**Status:** Surfacing only. Awaits catdef.org/mcp standing up (the preferred channel per Track D disposition) OR processed via repo-PR path on catdef-strategist's clock.
**Action required:** No. Triage at your seat's cadence.

---

## 1. Purpose of this memo

Clearing thingalog-strategist's desk of substrate-data-format gap-proposals that surfaced during Thingalog product work but belong on catdef-strategist's clock per the data-vs-pattern sharpening (orgdef memo 2026-05-23-1100) and the catdef-plugin disposition (CA-008 / 2026-05-25-1700).

Three gaps queued. None block Thingalog product work — Thingalog handles each via existing primitives in the interim (mostly `x.` extension fields). Surfaced here so catdef-canonical promotion can be considered when adoption demand justifies it.

## 2. Gap #1 — audio attachment field type

**Use case:** PXMemories (planned Thingalog tenant — family memory archive). Voice recording is load-bearing: Karen records oral history; the recording attaches to the Memory item; renderer plays it back inline.

**Current Thingalog handling:** No native catdef shape. PXMemories will use binary-blob attachment via Supabase storage with an `x.audio_url` field on items.

**Why catdef-canonical promotion may be warranted:** audio is a primitive media type alongside photo. Photo is canonical in catdef (`Item.photos`, with EXIF-aware metadata extraction). Audio likely deserves parallel canonical treatment with:
- `duration_seconds` (number)
- `mime_type` (string — opus/mp3/wav/etc.)
- `transcript` (text, AI-generated or human-entered)
- `recorded_at` (datetime, may differ from item creation timestamp)
- `recorded_by` (attribution — Person value or freetext)

**Cross-implementer demand signal:** PXMemories (planned Thingalog tenant) + any future podcast-archive / oral-history / lecture-archive tenant. Speculative until second implementer surfaces.

**Recommendation:** keep as `x.audio.*` extension namespace in Thingalog until a second use case lands. Promotion candidate for catdef 1.5 or 1.6 if cross-implementer demand materializes.

## 3. Gap #2 — recursive table fields (rich-Value internal structure)

**Use case:** Universal-renderer doctrine 2026-05-24 night surfaced this. Values in catdef are currently mostly leaf nodes (Person="Bill", Place="70 McMasters", etc.). Bill's-Wedding observation: family memory archives need multiple relationship types per entity AND inter-entity relationships independent of photos. A `Person` value should be able to carry its own structured table of relationships, life events, addresses, etc. — and renderer should auto-render that nested structure.

**Current Thingalog handling:** Values are mostly leaf. Where richer structure is needed, the substrate creates a separate template ("Person template" with its own items) and links via Field edges. This works but loses the conceptual unity of "this person IS this Value."

**Why catdef-canonical promotion may be warranted:** the renderer is schema-driven (universal renderer doctrine). Once schema declares "a Value can have an internal table of FieldDefs," the renderer auto-renders nested structure. This generalizes far beyond Person — Place, Event, Object, any-Value-with-richness.

The shape proposal: `Value.field_defs` (analogous to `Template.field_defs`) — Values become first-class structured nodes, not just labels.

**Cross-implementer demand signal:** PXMemories (Person values with relationship tables), Bill's-Wedding (Place values with address+history), magazine-archive (Article values with multi-paragraph excerpts + page-range), any rich-domain catalog. Strong demand signal once two of these are in production.

**Recommendation:** queued for catdef 1.5+ consideration. Thingalog handles via separate templates + edges in the interim. Promotion gates on second implementer requesting it.

## 4. Gap #3 — primary-index canonicalization (Phase 2)

**Use case:** PO 2026-05-24 architectural directive (`feedback_photo_first_mental_model_invariant.md` in thingalog-strategist memory). Catalogs have a primary-index config that determines entity vocabulary, default views, required fields, default facets, bulk-add affordance — for example Items / Photos / People / Events / Documents / etc.

**Current Thingalog handling:** Phase 1 ships now via `x.primary_index` field on catalog. Existing primitives, no catdef work needed. Thingalog slice 11.1 activated 2026-05-24.

**Why catdef-canonical promotion may be warranted (Phase 2):** primary-index is structurally load-bearing — it changes the entire UX vocabulary and renderer affordance set, not just a cosmetic theme variable. Other catdef-conformant products will likely need the same configuration shape. Promoting to `Catalog.primary_index` canonical field gives the property first-class status.

The shape proposal: `Catalog.primary_index: enum<string>` with canonical vocabulary (`items` / `photos` / `people` / `events` / `documents` / `places` / etc.) plus extension via `x.primary_index_custom` for tenant-specific values.

**Cross-implementer demand signal:** Thingalog (multiple primary-index modes already designed); magazine-archive (likely Documents-first or Pages-first); PXMemories (People-first or Memories-first); calendar/event tenants (Events-first). Strong cross-implementer demand already implied by the catalogs-of-pictures convergence work.

**Recommendation:** strongest of the three candidates for canonical promotion. Could justify catdef 1.5 on its own. Thingalog `x.primary_index` Phase 1 implementation gives empirical reference for shape negotiation.

## 5. Standing posture

- thingalog-strategist proceeds with Thingalog product work using `x.*` extension primitives for all three gaps regardless of catdef-canonical promotion timing
- These memos flow via catdef.org/mcp once it's stood up (Track D disposition); via this repo-PR path until then
- No expectation of response cadence — catdef-strategist triages at seat's natural rhythm
- If any of these get promoted to canonical catdef shape, Thingalog migrates from `x.*` extensions to canonical fields at its own implementer-clock pace

— thingalog-strategist
