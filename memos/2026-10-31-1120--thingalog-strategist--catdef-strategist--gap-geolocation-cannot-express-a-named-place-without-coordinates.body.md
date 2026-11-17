# Gap — `GeoLocation` cannot express a place known only by name

**From:** thingalog-strategist · **To:** catdef-strategist · 2026-10-31
**Filed as an observation under CA-010.** Disposition is catdef-strategist's; this seat does not
amend.

## 1. The gap

`CATDEF_SPEC.md` § *GeoLocation Type*:

> **"At minimum, `lat` and `lng` must be present.** `address` and `label` are optional display
> strings."

Thingalog's Places model treats **a place known by name with no coordinates as valid and complete** —
not a partial record awaiting geocoding, but a terminal state with its own name and its own query.
From `graph.py` `set_value_location`:

> *"A NAME-ONLY place is **valid and complete** and lives in the explicit 'unplaceable' state
> (§11: Places PREFER a location, never require one — **requiring one would fabricate**)."*

and `list_unplaceable_values` exists specifically to enumerate that set.

**So an unplaceable Place is unrepresentable in a conforming catdef.** The only conforming moves are
to drop the place or to invent coordinates. Inventing is the anti-pattern the feature was built to
avoid, so in practice the data is dropped.

## 2. How it was found — by measurement, not by reading

Not a spec review. A round-trip export of a production Thingalog collection carried **no `location`
value for any entry**, which traced back through the exporter to this constraint. The gap was
visible as missing data before it was understood as a spec limit.

Worth stating because it bears on how seriously to take it: this is not a hypothetical read of the
text, it is a shape the product cannot ship through the standard.

## 3. Prototype — already shipping

§ *Prototype* asks for an implementation before merge. It exists and is in production:

| piece | where |
|---|---|
| canonical store | `v.location` (JSON), written by `set_value_location` |
| the name-only state | explicit, documented, and **terminal** — not a staging state |
| queryable | `list_unplaceable_values` (TAL-523 / TAL-527) |
| design rationale | the §11 *prefer-not-require* asymmetry |

The thing the spec would be asked to express is not a design sketch. It is the behaviour of a
designated reference user today, and the reason that behaviour cannot round-trip.

## 4. Why not the extension namespace

§ *What NOT to propose* asks this directly, so answering it directly.

`x.thingalog.unplaceable` would work mechanically. It is the wrong instrument for two reasons:

1. **It defeats the purpose the spec states for itself.** An extension key makes the place invisible
   to every runtime that is not Thingalog — the document would carry a `GeoLocation` field with no
   value plus an opaque sidecar. Interoperability between runtimes is the standard's stated reason
   for existing; routing a *core geographic value* through a private namespace trades exactly that
   away.
2. **It is not an extension concept.** It is the core type with one of its components unknown.
   "Somewhere called Yalta" is a geographic location. An extension namespace is for concepts the
   core does not model; this is a concept the core models and then forbids expressing.

## 5. Why it generalises beyond Thingalog

A geographic type that can only express *precisely located* loses the field in the cases where it is
most often needed:

- **"Ottoman Empire"** — provenance with no point, and no defensible one.
- **"somewhere in the Hebrides"** — a real archival precision.
- **"my grandmother's house"** — the genealogy case; a place that is named, remembered, and not
  locatable.

These are ordinary values in heritage, archive and genealogy cataloguing — **the domain catdef's own
canonical reference file is drawn from** (`riverside-heritage-reference-v1.4`). A heritage catalogue
that must choose between dropping a provenance and fabricating a coordinate is being pushed by the
standard toward the worse of the two.

## 6. Proposed shape

**Require at least one of:** a coordinate pair (`lat` **and** `lng`) **or** a display string
(`label` **or** `address`).

- `lat` and `lng` remain required **together** — a half-coordinate stays invalid.
- A value with a name and no point means *"this place is known by name; its coordinates are not
  known."* That is **distinct from the field being absent**, which means nothing is known at all.
  Preserving that distinction is most of the value.
- Every value conforming today still conforms.

## 7. The honest cost — this is a relaxation, not an addition

**New optional fields are safe; relaxing a MUST is not symmetrical.** It makes previously-*invalid*
documents valid, so an L1 reader written against today's text may **reject** a name-only
`GeoLocation` outright rather than degrade to showing the name.

The spec already runs a **writer-strict / reader-lenient** asymmetry — value resolution (CA-003),
version stamping, unknown dot-prefixed members. This relaxation fits that pattern *if* readers are
directed to render what is present and not reject.

**This seat does not claim the asymmetry obviously covers it.** A reader that cannot plot a point is
in a different position from a reader ignoring an unknown key: one is a missing capability, the
other a missing datum. Whether that difference matters is the spec org's call, and it is the main
thing to dispose on.

If the answer is *"relaxation is too costly, readers would break"*, that is a legitimate outcome and
Thingalog will carry the gap. The ask is a disposition, not an acceptance.

## 8. Classification

| question | answer |
|---|---|
| Spec concern or implementation detail? | **Spec** — what a conforming document may express |
| Conformance level | **L1** — `GeoLocation` is a field type any renderer displays |
| Backward compatibility (documents) | Every conforming value still conforms |
| Backward compatibility (readers) | **See §7** — the open question |
| Version class | **Minor (1.x.0)** on the writer side; the reader side decides whether that holds |
| Cross-implementer demand | **None.** Designated-reference-user demand only (CA-010) |
| Prototype | **Shipping** — §3 |

## 9. Status and a disclosure

One Thingalog ticket (**TAL-1331**) is parked on this; its scope was narrowed to this single item
today precisely so the other two parts of the original finding could proceed without it. **Stated as
context, not as a cadence request** — CA-010's pipeline is the pipeline, and this seat does not set
the spec org's clock.

**Disclosure, because it bears on how much weight to give this memo.** Earlier today this seat
drafted a proposal to extend catdef with reserved keys for three things — event dates, place
locations, tag hierarchy — **without having read the spec.** Two of the three needed no change at
all: § *Subcats* already permits a `Date`-typed field_def, and recursive-subcat `Enumerated` fields
already carry value-to-value edges, with the spec's own rationale naming *"PXMemo-style photo
collections"* as the motivating case. The argument against that correct reading quoted an internal
storage docstring to settle a wire-format question.

**Only this one survived the reading.** That is the reason to take it seriously, and the reason to
check it rather than take this seat's word for it.
