# Proposal: i18n via polymorphic translatable fields

**Status:** Draft
**Target version:** 1.4 (minor — introduces polymorphic translatable fields, a closed policy registry, and value #9 governance)
**Origin:** Known work item from CLAUDE.md; Scott Welch prior art from Edsby (day-job localization work).
**Strategist decision:** [decisions/i18n-polymorphic-fields.md](../decisions/i18n-polymorphic-fields.md) — accept with modifications, including governance-level adoption of value #9; this revision applies them.
**Conformance level affected:** L1 (passthrough) / L2+ (locale-aware selection). Policy compliance is a gating conformance dimension across all levels (value #9).

## Summary

This proposal does two things at once, because they are inseparable:

**1. It establishes catdef as a policy-bearing standard.** Alongside the existing dimensions of structure (fields, types, subcats) and content (values), catdef now formally carries **policy** — author-declared constraints on how downstream tools must handle the content. Policy compliance is a conformance requirement: a runtime that silently ignores a declared policy is not a conformant catdef implementation, regardless of how well it handles the other dimensions. The conformance suite gains a policy-compliance test category as a first-class concern. This is formalized as value #9 in the maintainer CLAUDE.md.

**2. It introduces the first two policies, scoped to internationalization.** Translatable string fields (labels, descriptions, prompts, etc.) become **polymorphic**: a field that currently accepts a string may alternately accept an object whose members are locale-keyed string variants plus author-declared policies. The simple form remains exactly as it is today; the object form is optional, invoked only when the catdef author actually needs multiple locales, translator context, or policy assertions such as "do not machine-translate."

The v1.4 work defines two policies (`.context`, `.machine-translate`) in the i18n scope. The category itself is expected to extend past i18n in later versions (redistribution, attribution, retention, consent, provenance) — flagged here as a v1.5+ concern.

Runtimes that don't understand the object form treat it as an unfamiliar value and fall through to the catdef's declared `primaryLocale` string (or skip the field). Runtimes that do understand it pick the viewer's locale, with well-defined fallback rules, and MUST respect any declared policies.

## Motivation

catdef today has no localization story. Non-English adopters face three bad options: publish a monolingual catalog in their own language (which excludes outside viewers), duplicate the entire catdef per locale (which fragments the source of truth), or shoehorn translations through the extension namespace (which offers no interoperability across runtimes).

At the same time, the majority of catdef authors are monolingual and will remain so. A localization design that forces every author to learn a keyed-translation schema violates value #8 (human-readable) and imposes cost on the common case for the benefit of the rare one.

The polymorphic-field design lets monolingual catdefs stay trivial and enables multilingual catdefs without adding a parallel schema.

## Proposed change

### Authoring pattern

**Simple form (unchanged, current behavior):**

```json
{
  "label": "Artist"
}
```

**Translated form (new, optional):**

```json
{
  "label": {
    ".context": "music-catalog",
    ".en": "Artist",
    ".fr": "Artiste",
    ".ja": "アーティスト"
  }
}
```

### Dot-prefix convention for i18n members

All reserved members inside a translatable-field object are **dot-prefixed** to mark them as translation metadata rather than data. Dot-prefixed members divide into two categories with distinct semantics:

#### Locale variants

One translated string per locale, keyed by a BCP-47 tag:

- `.en` — English
- `.fr` — French
- `.en-GB` — British English
- `.zh-Hant` — Traditional Chinese

Strict BCP-47 recommended but not validated at L1. Runtimes resolve locale variants using RFC 4647 §3.4 (Lookup) against the available variants; see §Fallback semantics below.

#### Policies

Statements of author intent about how the field's content must be handled by any tool or runtime that processes it. Policies travel with the data. A downstream tool that reads the catdef inherits the policies and **MUST** respect them, even if the tool was not originally aware of them.

**Policy compliance is a conformance requirement** (see maintainer value #9). An implementation that renders structure and content correctly but ignores declared policies — for instance, by silently auto-translating a field marked `.machine-translate: "Never"` — is **not conformant**. The conformance suite will gate policy-compliance checks as a first-class test category, alongside field-type support and forward-compatibility behavior.

All policies are reserved identifiers defined by the core spec. The policy vocabulary is **closed and registered**: adopters cannot introduce new policies via the extension namespace (they would not interoperate, which defeats the purpose — a policy that only some tools respect is worse than no policy). Future policy additions are explicit spec changes with their own proposals.

#### Policy Registry (v1.4)

The registry below defines every policy a conformant runtime MUST recognize. Runtimes resolve dot-prefixed keys by first matching against the registry (by exact name); unregistered dot-prefixed keys are classified by the BCP-47 shape heuristic as a secondary mechanism (see "Unknown dot-prefixed members" below).

**Implemented in v1.4:**

| Policy | Values | Registered | Semantics |
|--------|--------|------------|-----------|
| `.context` | free-form string | 1.4 | Disambiguator for translators. Example: `"music-catalog"` tells a translator choosing between multiple French words for "Record" that this is about a recording artist, not a medical record. Advisory to renderers; normative for translation tooling that reads the object. Carried with the object so it reaches translation tooling. |
| `.machine-translate` | `"Allow"` \| `"Never"` | 1.4 | Default is `"Allow"`. When `"Never"`, translation tooling MUST NOT auto-generate missing locale variants via machine translation, and the runtime MUST mark the rendered content as non-translatable using `translate="no"` (see §Conformance tests ft-i18n-09 for the normative mechanism). A tool encountering a missing locale for a `.machine-translate: "Never"` field SHOULD either surface the primary-locale variant or prompt for human translation; it MUST NOT silently insert an ML-generated translation. Use case: culturally-specific content (family stories, art provenance, specialized terminology, named entities) where machine translation produces plausible-looking but incorrect output. |

**Reserved for later proposals (named but not implemented in v1.4):**

| Policy | Planned purpose |
|--------|-----------------|
| `.plural` | pluralization rules |
| `.gender` | grammatical-gender variants |
| `.dir` | per-locale text direction (LTR / RTL / auto) |

A runtime encountering a reserved-but-unimplemented policy MUST ignore it without error; implementations arriving ahead of the spec are non-conformant in either direction (rejecting it is wrong; acting on undefined semantics is also wrong).

#### Dot-prefix convention summary

The dot prefix serves three functions: it marks the member as translation metadata rather than a locale code or field name, it namespaces the reserved vocabulary away from author-chosen field names, and it gives parsers a classification rule — **registered policies** first (from the Policy Registry above), then **locale variants** (any remaining dot-prefixed key; BCP-47 shape recommended), then **unknown policies** (warn but do not error). This registry-first classification is normative; the BCP-47-shape check is a secondary heuristic for forward compatibility.

#### Unknown dot-prefixed members

A runtime encountering a dot-prefixed key it does not recognize applies the following rules, consistent with value #5 (forward compatibility) and the writer-strict / reader-lenient pattern established by CA-002 and CA-003:

- **Unknown locale variant** (dot-prefixed key matching BCP-47 shape that the runtime does not need) — ignore silently. The viewer's locale will not be served by this variant, but neither is anything broken.
- **Unknown policy** (dot-prefixed key not in the Policy Registry and not BCP-47-shaped) — warn but tolerate. Never error on a forward-compatible extension. A future policy the runtime doesn't yet know about is strictly safer to preserve than to strip.
- **Writer obligation** — writers MUST NOT emit a dot-prefixed key that is neither in the Policy Registry nor a valid BCP-47 locale tag. Writer-side validators reject unknown dot-prefixed keys explicitly.

This is the same strict-writer / lenient-reader asymmetry used throughout the v1.4 bundle.

#### Extension-field translatability

Extension fields (`x.<domain>.<identifier>`) MAY use the polymorphic-translatable-field pattern at the extension author's option. The core spec does not mandate; extension authors choose per-field whether to support translatable values.

**Worked example.** An extension defines `x.museum.description` for exhibit descriptions. The extension author opts into polymorphic translatability:

```json
{
  "x.museum.description": {
    ".context": "exhibit-label",
    ".machine-translate": "Never",
    ".en": "The earliest known cuneiform tablet from this region, c. 2400 BCE.",
    ".fr": "La plus ancienne tablette cunéiforme connue de cette région, vers 2400 AEC."
  }
}
```

A conformant runtime encountering an extension field it doesn't recognize already ignores the field per the extension-namespace rules; a runtime that DOES recognize the extension and finds a polymorphic value applies the same resolution machinery as core translatable fields.

**A note on scope.** The v1.4 proposal introduces policies only within the context of translatable fields. The broader question of whether policies as a category extend to non-i18n concerns (redistribution, attribution, retention, consent, provenance, sensitivity) is explicitly out of scope for this proposal but is expected to follow in later versions. The v1.4 work establishes the category and the syntactic pattern; future proposals populate it. The conformance machinery built for v1.4 policy compliance will generalize to v1.5+ policies without rework.

### Worked examples

**Monolingual, simple:**

```json
{
  "label": "Artist"
}
```

**Bilingual with translator context:**

```json
{
  "label": {
    ".context": "music-catalog",
    ".en": "Artist",
    ".fr": "Artiste"
  }
}
```

**Named entity with no-machine-translate policy:**

```json
{
  "band": {
    ".machine-translate": "Never",
    ".en": "Rolling Stones"
  }
}
```

A translation tool encountering this field MUST NOT auto-translate `"Rolling Stones"` to any other locale. The band's name is *its name* — not a string to be localized. This is an author-declared policy; the tool that respects it is conformant; the tool that ignores it is not.

**Culturally-specific content with no-machine-translate policy:**

```json
{
  "description": {
    ".machine-translate": "Never",
    ".en": "My grandmother told this story every Christmas. It changed each time, but the ending was always the same."
  }
}
```

A French-locale viewer sees the English primary-locale variant until a human translator provides a `.fr` version. Machine translation of personal-memoir content produces confidently-wrong output that damages the archive's integrity; the policy prevents it.

### Primary locale declaration

A catdef using translatable fields SHOULD declare its primary locale at the top level:

```json
{
  "catdef": "1.4",
  "primaryLocale": "en",
  ...
}
```

If `primaryLocale` is omitted, the first locale encountered in any translatable field is treated as primary (undefined order; authors should declare explicitly).

### Fallback semantics

Runtimes resolve locale variants using **RFC 4647 §3.4 (Lookup)** against the available locale variants. The catdef's `primaryLocale` is the default if no variant matches via Lookup. Last-resort fallback to any defined variant, with implementation-defined order, MUST emit a warning.

RFC 4647 §3.4 is the standard algorithm for progressively shortening a BCP-47 language tag (e.g., `fr-CA` → `fr` → default). Using it directly avoids edge-case bugs in hand-rolled fallback implementations and gives implementers an off-the-shelf reference.

At no point does the runtime invent a translation it doesn't have. It selects from what's present.

### Which fields are translatable

All user-facing string fields in the core spec are candidates. Conservative v1.4 list:

- `label` (on fields, subcats, enums, collections)
- `description` / `prompt` (on fields)
- `title` (on the catdef itself, on collections)

**Explicitly not translatable (at least in v1.4):**

- Field `id`, `name`, `type` — identifiers, not text
- Numeric / Date / Money values — formatting is the runtime's job (see below)
- URLs — may become translatable later; out of scope here
- **Enumerated field values at item level** — identifiers, not text. Translated displays are achieved via the subcat-label workaround described below; item-level enum-value shape polymorphism is deferred to v1.5 (see Open Questions).

### Translating enum value displays

Enum values in catdef are **identifiers** — stable keys that reference subcat records. Making them shape-polymorphic per-locale would hurt portability (a French and an English catdef would key the same logical entity differently) and conflate identifier with display. The correct shape for translated enum displays in v1.4 keeps the identifier stable and moves the polymorphism one level down, onto a subcat Label field.

**Pattern:**

```json
{
  "subcats": {
    "Manufacturer": {
      "field_defs": [
        {"label": "DisplayName", "type": "String"}
      ],
      "values": {
        "Stanley": {
          "DisplayName": {".en": "Stanley", ".ja": "スタンレー"}
        },
        "Omega": {
          "DisplayName": {".en": "Omega", ".ja": "オメガ"}
        }
      }
    }
  }
}
```

The identifier (`"Stanley"`, `"Omega"`) stays stable. The display value uses the v1.4 polymorphic-translatable-field pattern applied to the subcat's `DisplayName` field. A runtime renders `subcats.Manufacturer.values["Stanley"].DisplayName` through the same locale-resolution machinery as any other translatable field, yielding `"Stanley"` for English viewers and `"スタンレー"` for Japanese viewers — while every reference to the value across the catalog keys the same identifier.

This is the canonical way to translate enum-valued fields without introducing item-level polymorphism. It works for any Enumerated field whose target is a subcat, which is the expected pattern for enum values that need translated displays.

### Locale-aware formatting of non-string types

**Explicitly deferred.** catdef declares that a field is Date, Money, or Number. How that value renders for a French-locale viewer (`49,00 $CA` vs. `$49.00 CAD`) is a **runtime concern**, resolved via standard library support for locale-aware formatting (CLDR). The spec does not dictate format strings or display conventions for numeric types.

### Backward compatibility

- Existing v1.x catdefs with plain-string labels remain valid at v1.4. No migration needed.
- Existing v1.x runtimes encountering a v1.4 catdef with object-form labels will, if properly implementing value #5 (forward compatibility), either ignore the unrecognized object value or surface an unknown-field warning. Either is acceptable. Both catdef and runtime continue to function for plain-string fields.
- A v1.4 runtime reading a v1.x catdef with plain-string labels renders them unchanged — the simple form is also the v1.x form.

### Release management

This proposal is bundle-locked with the v1.4 release (CA-001, CA-002, CA-003, CA-006). Rationale:

- Value #9 is a governance change that reshapes the conformance surface; shipping it outside the v1.4 bundle would fragment the constitutional layer of the spec.
- The polymorphic-translatable-field pattern introduces new normative obligations on writers (Policy Registry membership, dot-prefix semantics) that v1.3 runtimes are not obligated to honor; coordination with CA-002's writer-strict stamping rule is load-bearing.
- Policy compliance (`ft-i18n-07`, `-08`, `-09`) is a new conformance-test category (`conformance/policies/`); introducing it mid-version would produce a spec in which the policy-compliance rule exists but its test harness doesn't.

Per the v1.4 release-management constraint shared with CA-001/002/003/006, merge-to-main is held until the full bundle is coherent. Branch advance and review-in-flight are fine.

## Conformance tests

Policy-compliance tests (ft-i18n-08, ft-i18n-09 below) are **gating** — a runtime or tool that fails them fails catdef conformance. This is a direct application of value #9 (policy compliance is a conformance requirement). Policy-compliance testing will establish a new test category in the conformance suite (`conformance/policies/`) that generalizes to future policy additions.

### L1 (passthrough)

- **ft-i18n-01**: An L1 renderer presented with a catdef containing a translatable `label` object MUST either (a) render the `primaryLocale` variant, or (b) log a warning and skip the field. It MUST NOT crash.
- **ft-i18n-02**: An L1 renderer presented with a monolingual catdef (plain-string labels, no `primaryLocale` declaration) behaves identically to a v1.3 renderer. No regression.

### L2+ (locale-aware selection)

- **ft-i18n-03**: Given a bilingual catdef (`.en` / `.fr`), a viewer in `en` locale sees English labels; a viewer in `fr` locale sees French labels.
- **ft-i18n-04**: Given a catdef with `.fr` but no `.en`, with `primaryLocale: "fr"`, a viewer in `en` locale sees French (primary fallback).
- **ft-i18n-05**: Given a catdef with `.fr` and no primary locale declared, a viewer in `en` locale sees the French variant (any-defined-locale fallback) and a warning is logged.
- **ft-i18n-06**: Given a catdef with `.fr-CA`, a viewer in `fr` sees the `fr-CA` variant (substring fallback).

### Policy compliance (GATING — conformance required)

- **ft-i18n-07**: The `.context` policy, when present, is preserved in any export or roundtrip, and is passed through unchanged to any translation tooling that reads the catdef. A tool that strips `.context` on export is non-conformant.
- **ft-i18n-08**: A translation tool presented with a field whose object contains `.machine-translate: "Never"` MUST NOT produce an ML-generated translation to populate missing locales. Verified by running the tool against a fixture and asserting no new `.<locale>` members are added to `.machine-translate: "Never"` fields. A tool that auto-translates such fields is non-conformant.
- **ft-i18n-09 (gating).** A runtime rendering `.machine-translate: "Never"` content MUST mark it as non-translatable using the HTML `translate="no"` attribute (or the platform-equivalent suppression mechanism for non-HTML renderers). The runtime MUST NOT itself offer in-runtime translation UI for `.machine-translate: "Never"` content. Suppression of OS-level browser translation features (Chrome auto-translate, Safari translate-on-page) is achieved by the `translate="no"` mechanism; runtimes that fail to emit the suppression marker are non-conformant. Verified by rendering a fixture with `.machine-translate: "Never"` and asserting the rendered DOM carries `translate="no"` on the corresponding nodes. For a viewer whose locale is not present in the object, the runtime MUST render the primary-locale variant (not a translation sourced elsewhere, and not a machine translation computed in-browser).

### Fixtures

- `bilingual-artist-catalog.catdef` — small multilingual fixture covering labels, descriptions, and one ambiguous term using `.context`.
- `monolingual-french.catdef` — single-locale non-English fixture to catch English-centric assumptions in runtimes.

## Alternatives considered

### Keyed-by-abstract-ID (classic i18n)

Industry-standard pattern: every UI string gets a key like `field.artist.label`, and translations are stored in separate per-locale files. Rejected because:

1. Violates value #8 (human-readable). A non-developer can no longer read a catdef and understand it.
2. Violates value #7 (one file, complete product). Translations live elsewhere; a catdef becomes dependent on companion files.
3. Goes stale: the key persists after the English copy changes, creating a lie. Scott Welch's 15-year experience with this pattern at Edsby (and earlier at FirstClass) confirms the staleness cost is real.
4. Translators work without context by default, producing worse translations.

### Sibling-key dotted convention (`label.fr: "Artiste"`)

Sketched in an earlier draft. Rejected because:

1. Scatters translation data across sibling keys rather than clustering it — worse for readability and for tooling that wants to grab "all translations of this label" in one scope.
2. Structural i18n (object-valued translatable fields) is preferable to naming-convention i18n (prefix-matching on keys). A validator can recognize the former by structure; the latter requires string-matching logic.

### Extension namespace only

"Leave i18n to `x.<org>.<identifier>`." Rejected because:

1. Every runtime would invent its own incompatible pattern. catdef's value as a portability layer erodes.
2. i18n is a sufficiently common need that it belongs in the core, not the extension namespace.

## Open questions

1. **Item-level enum-value shape polymorphism.** **Deferred to v1.5 with a documented workaround.** v1.4 handles translated enum displays via the subcat-label workaround described in §Translating enum value displays — the identifier stays stable and the display moves to a subcat `Label` field (or equivalent), which uses the v1.4 polymorphic-translatable-field pattern. Whether item-level polymorphism on Enumerated values is a feature catdef wants at all is a v1.5 strategy question; the subcat-label workaround may obviate the need entirely.

2. **Pluralization and gender.** Some locales require different strings based on count or grammatical gender. Out of scope for v1.4 (policy names reserved, semantics deferred to a later proposal).

3. **RTL text direction.** `.dir` is reserved for v1.4 but unimplemented. Default runtime behavior should use CSS `dir="auto"` or equivalent. Explicit per-locale `.dir` override deferred unless adopter feedback surfaces the need.

4. **Catdef-level locale negotiation for L2+.** When a catdef contains every locale's copy of every field, an L2+ server could choose to deliver only the viewer's locale to save bandwidth. This is a CATIO_SPEC.md concern more than a CATDEF_SPEC.md concern. Flagged here so transport-spec proposals can reference this one.

5. **Policies beyond i18n — scope for a follow-on proposal.** The v1.4 work introduces *policy* as a category, scoped to translation-adjacent concerns. Policies as a general mechanism — author-declared constraints on how any field's content must be handled by downstream tools — appear to have broad applicability (redistribution, attribution, retention, consent, sensitivity, provenance). A v1.5 proposal should be opened to work out which non-i18n policies belong in the core and which in the extension namespace. Flagging here so the follow-on work is visible from the i18n proposal's context. Recommended follow-on proposal title: *"Field-level policies: author-declared constraints on downstream handling."*

Resolved during i18n-revisions:

- Extension-field translatability (prior OQ5) → promoted to normative in §Extension-field translatability with a worked example.
- Validator behavior on unknown dot-prefixed members (prior OQ6) → promoted to normative in §Unknown dot-prefixed members; aligned with the strict-writer / lenient-reader pattern from CA-002/003.
- Default value of `.machine-translate` (prior OQ7) → resolved as `"Allow"`. Rationale: catdef adoption depends on monolingual authors getting useful translations by default. The opt-in burden falls on authors of culturally-specific content, who are the ones who think about translation policy explicitly; explicit opt-in is low-cost for the affected case. The canonical demonstrates `.machine-translate: "Never"` as documented best practice for narrative / culturally-specific fields (canonical-builder brief, not part of this proposal).

## Requested maintainer actions

**This proposal contains a governance-level change** (adding value #9 to the maintainer values-that-don't-move) in addition to the i18n feature work. The governance sign-off is recorded in [decisions/i18n-polymorphic-fields.md §Governance decision](../decisions/i18n-polymorphic-fields.md). The spec-text application lands in the v1.4 editorial PR (tagged with a "governance-change" marker).

- **Apply value #9 to CLAUDE.md §Values that don't move** — "Policy compliance is a conformance requirement" — and update §Success criteria item 6 to reference value #9 explicitly.
- Apply the polymorphic-field pattern and closed Policy Registry to CATDEF_SPEC.md, per the §Proposed change section of this proposal.
- Scaffold `conformance/policies/` as the new test category; initial inhabitants are `ft-i18n-07`, `ft-i18n-08`, `ft-i18n-09`.
- Apply the registered v1.4 Policy Registry entries (`.context`, `.machine-translate`) and the reserved-but-unimplemented list (`.plural`, `.gender`, `.dir`).
- Acknowledge the follow-on proposal signaled in Open Question 5 (field-level policies beyond i18n) as work to be scheduled for v1.5 planning.
- Acknowledge Open Question 1 (item-level enum-value polymorphism) as v1.5 work with the subcat-label workaround as the documented v1.4 path.
