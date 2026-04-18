# Proposal: i18n via polymorphic translatable fields

**Status:** Draft
**Target version:** 1.4 (next minor)
**Origin:** Known work item from CLAUDE.md; Scott Welch prior art from Edsby (day-job localization work).
**Conformance level affected:** L1 (passthrough) / L2+ (locale-aware selection)

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

Strict BCP-47 recommended but not validated at L1. Runtimes fall back via substring match (`.fr-CA` falls back to `.fr`; `.fr` falls back to `.primaryLocale`; last resort, any defined variant).

#### Policies

Statements of author intent about how the field's content must be handled by any tool or runtime that processes it. Policies travel with the data. A downstream tool that reads the catdef inherits the policies and **MUST** respect them, even if the tool was not originally aware of them.

**Policy compliance is a conformance requirement** (see maintainer value #9). An implementation that renders structure and content correctly but ignores declared policies — for instance, by silently auto-translating a field marked `.machine-translate: "Never"` — is **not conformant**. The conformance suite will gate policy-compliance checks as a first-class test category, alongside field-type support and forward-compatibility behavior.

All policies are reserved identifiers defined by the core spec; adopters cannot introduce new policies via the extension namespace (they would not interoperate, which defeats the purpose — a policy that only some tools respect is worse than no policy).

Policies defined in v1.4 (scoped to the i18n feature set):

- **`.context`** — Free-text disambiguator for translators. Example: `"music-catalog"` tells a translator choosing between multiple French words for "Record" that this is about a recording artist, not a medical record. Advisory to renderers; normative for translation tooling that reads the object. Carried with the object so it reaches translation tooling.
- **`.machine-translate`** — Value is `"Allow"` (default, omittable) or `"Never"`. When `"Never"`, translation tooling MUST NOT auto-generate missing locale variants via machine translation, and runtime in-browser translation features MUST NOT translate the rendered content. A tool encountering a missing locale for a `.machine-translate: "Never"` field SHOULD either surface the primary-locale variant or prompt for human translation; it MUST NOT silently insert an ML-generated translation. Use case: culturally-specific content (family stories, art provenance, specialized terminology, named entities) where machine translation produces plausible-looking but incorrect output.

Policies reserved for later proposals (not implemented in v1.4):

- `.plural` — pluralization rules
- `.gender` — grammatical-gender variants
- `.dir` — per-locale text direction (LTR / RTL / auto)

The dot prefix serves three functions: it marks the member as translation metadata rather than a locale code or field name, it namespaces the reserved vocabulary away from author-chosen field names, and it gives parsers a single syntactic rule to distinguish variants (`.<language>`) from policies (`.<keyword>`) — variants are BCP-47-shaped; policies are not.

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

A runtime rendering a translatable field for a given viewer locale follows this order:

1. **Exact match** (`.fr-CA` for viewer `fr-CA`)
2. **Language match** (`.fr` for viewer `fr-CA`)
3. **Primary locale** (whatever the catdef declared)
4. **Any defined locale**, implementation-defined order (last resort; should log a warning)

At no point does the runtime invent a translation it doesn't have. It selects from what's present.

### Which fields are translatable

All user-facing string fields in the core spec are candidates. A conservative first pass:

- `label` (on fields, subcats, enums, collections)
- `description` / `prompt` (on fields)
- `title` (on the catdef itself, on collections)
- String enum values (via a separate pattern; see Open Questions)

**Explicitly not translatable (at least in v1.4):**

- Field `id`, `name`, `type` — identifiers, not text
- Numeric / Date / Money values — formatting is the runtime's job (see below)
- URLs — may become translatable later; out of scope here

### Locale-aware formatting of non-string types

**Explicitly deferred.** catdef declares that a field is Date, Money, or Number. How that value renders for a French-locale viewer (`49,00 $CA` vs. `$49.00 CAD`) is a **runtime concern**, resolved via standard library support for locale-aware formatting (CLDR). The spec does not dictate format strings or display conventions for numeric types.

### Backward compatibility

- Existing v1.x catdefs with plain-string labels remain valid at v1.4. No migration needed.
- Existing v1.x runtimes encountering a v1.4 catdef with object-form labels will, if properly implementing value #5 (forward compatibility), either ignore the unrecognized object value or surface an unknown-field warning. Either is acceptable. Both catdef and runtime continue to function for plain-string fields.
- A v1.4 runtime reading a v1.x catdef with plain-string labels renders them unchanged — the simple form is also the v1.x form.

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
- **ft-i18n-09**: A runtime rendering a `.machine-translate: "Never"` field for a viewer whose locale is not present in the object MUST render the primary-locale variant (not a translation sourced elsewhere, and not a machine translation computed in-browser). A runtime that offers in-browser translation on `.machine-translate: "Never"` content — regardless of user opt-in — is non-conformant.

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

1. **Enum values — reconciliation with existing polymorphism.** Enumerated types on subcat edges already support polymorphic value-objects in the current spec. The v1.4 work should *not* introduce a second, parallel polymorphism pattern for enum values on regular fields — it should reconcile with the existing edge-level pattern, applying the same shape. Concrete actions: (a) document the existing subcat-edge enum polymorphism in CATDEF_SPEC.md if it isn't already explicit there, (b) extend the same pattern to enum values in regular fields, (c) confirm that the dot-prefix convention (`.en`, `.fr`, `.context`, `.machine-translate`) works identically in both places. No new polymorphism; just extension of the existing one.

2. **Pluralization and gender.** Some locales require different strings based on count or grammatical gender. Out of scope for v1.4 (policy names reserved, semantics deferred to a later proposal).

3. **RTL text direction.** `.dir` is reserved for v1.4 but unimplemented. Default runtime behavior should use CSS `dir="auto"` or equivalent. Explicit per-locale `.dir` override deferred unless adopter feedback surfaces the need.

4. **Catdef-level locale negotiation for L2+.** When a catdef contains every locale's copy of every field, an L2+ server could choose to deliver only the viewer's locale to save bandwidth. This is a CATIO_SPEC.md concern more than a CATDEF_SPEC.md concern. Flagged here so transport-spec proposals can reference this one.

5. **Extension fields (`x.<domain>.<identifier>`).** Are extension field values translatable? My instinct: yes, using the same polymorphic pattern, at the extension's option. The core spec doesn't mandate; the extension author chooses. Confirm with a usage example.

6. **Validator behavior on unknown dot-prefixed members.** If a v1.4 runtime encounters an unrecognized dot-prefixed key (either a locale it doesn't support, or a future policy like `.plural`), does it ignore, warn, or error? Recommendation: ignore locale variants it doesn't need; warn-but-tolerate unknown policies; never error on a forward-compatible extension. Consistent with value #5.

7. **Default value of `.machine-translate`.** The draft says the default is `"Allow"` (i.e., tools may auto-translate unless told not to). Is this the right default? An argument for flipping to `"Never"` default: catdef is often used for culturally-specific content where the author may not have thought about translation policy explicitly, and the safer default is *don't auto-translate without permission*. Counterargument: `"Allow"` is permissive and matches the "no surprises for simple authors" ethos. Maintainer call.

8. **Policies beyond i18n — scope for a follow-on proposal.** The v1.4 work introduces *policy* as a category, scoped to translation-adjacent concerns. Policies as a general mechanism — author-declared constraints on how any field's content must be handled by downstream tools — appear to have broad applicability (redistribution, attribution, retention, consent, sensitivity, provenance). A v1.5 proposal should be opened to work out which non-i18n policies belong in the core and which in the extension namespace. Flagging here so the follow-on work is visible from the i18n proposal's context. Recommended follow-on proposal title: *"Field-level policies: author-declared constraints on downstream handling."*

## Requested maintainer actions

**This proposal contains a governance-level change (adding value #9 to the maintainer values-that-don't-move) in addition to the i18n feature work. Maintainer sign-off on the governance change is required before the feature work proceeds.**

- **Sign off on value #9** — "Policy compliance is a conformance requirement." This formalizes catdef as a policy-bearing standard and creates a new conformance-gate dimension. All future proposals touching policy behavior will reference this value.
- Sign off on the polymorphic-field approach as the v1.4 direction (vs. alternatives listed above).
- Sign off on the **variants / policies split** in the dot-prefixed namespace. This shape is load-bearing for future policy additions.
- Sign off on **policies as a closed vocabulary** (spec-defined only, not adopter-extensible). Open-vocabulary policies would defeat the interoperability guarantee.
- Decide on the "which fields are translatable" list for v1.4. The conservative list above is a starting point; could be expanded or contracted.
- Decide default for `.machine-translate`: `"Allow"` (permissive, matches monolingual-author ethos) or `"Never"` (conservative, safer for culturally-specific content). See open question 7.
- Review the fallback semantics; the fallback chain has design choices embedded in it that need maintainer concurrence.
- Acknowledge the follow-on proposal signaled in open question 8 (field-level policies beyond i18n) as work to be scheduled for v1.5 planning. No commitment required now; just a flag that the scope extends past v1.4.
