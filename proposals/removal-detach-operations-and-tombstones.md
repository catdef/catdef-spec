# Proposal: Removal — detach operations and the `data.tombstones` member

**Status:** Draft — **not merge-ready.** `CONTRIBUTING.md` §3 requires a prototype in at least one implementation; thingalog has accepted that work ([CA-023](../decisions/CA-023.md) Call 2) and it is not yet built. This artifact exists so the prototype is built against a shape rather than inventing one.
**Target version:** 1.5 (minor — two new write operations, one new optional `data` member; no existing document becomes invalid, no existing reader breaks)
**Origin:** [memos/2026-11-25-1927 thingalog-strategist](../memos/2026-11-25-1927--thingalog-strategist--catdef-strategist--gap-catx-as-storage-tier-comments-tombstones-canonical-bytes.body.md) §3.2 → [CA-022](../decisions/CA-022.md) Call 2 (accepted as a defect, separate-member constraint) → [memos/2026-11-25-2051](../memos/2026-11-25-2051--thingalog-strategist--catdef-strategist--correction-notes-are-items-and-an-offer-of-the-tombstone-prototype.body.md) §3.1 (edges) → [CA-023](../decisions/CA-023.md) Call 3 (escalated: CATIO has no detach operation at all)
**Conformance level affected:** L1 and above. L1 is unaffected in capability — a 1.4 L1 reader ignores the new member and renders live things only, which is correct behaviour, not degraded behaviour.

## Summary

catdef can express that a thing was *added* and *modified*, and that a value or photo was *attached*. It cannot express that any of them was *removed*.

This proposal closes that in two parts:

1. **`detach_value` and `detach_media`** are added to CATIO's write-operation table, which currently specifies `classify_thing` (attach values) and `attach_media` (attach photos) with **no detach counterpart of any kind.**
2. **`data.tombstones`**, a new optional member, serializes the outcome of removal — for things and for edges — so that a soft delete survives a round-trip instead of being silently discarded.

The two are one change. Serializing the outcome of an operation the spec does not name is incoherent, and naming an operation whose outcome cannot be written down reproduces the defect this proposal exists to fix.

## Motivation

### The spec specifies an operation and cannot represent its result

`CATIO_SPEC.md:151` defines `remove_thing` — *"Soft-delete a thing (trash)"* — mapped to `DELETE /api/items/{id}` and the `trash_item` MCP tool. Nothing in the serialized document represents the result. Two conformant runtimes can therefore disagree about whether a trashed thing exists, which is the interoperability ambiguity `CONTRIBUTING.md` lists under what SHOULD be proposed.

**This requires no demand to justify.** It is the spec contradicting itself, which is a stronger basis than an adopter asking.

### The operation vocabulary is asymmetric, and the implementations already noticed

CATIO's complete write-operation table:

| Operation | Direction |
|---|---|
| `import_thing`, `import_collection`, `import_catalog` | add |
| `update_thing` | modify |
| `classify_thing` — attach enumerated values | **attach** |
| `attach_media` — add a photo | **attach** |
| `remove_thing` — soft-delete a thing | remove (**things only**) |

A grep of `CATIO_SPEC.md` for *detach*, *unlink*, *edge* or *relationship* returns nothing.

**The reference implementations already expose the missing operations.** `detach_value` and `detach_photo` are live MCP tools on the running `airtrov` and `welch-family-tree` surfaces, observed directly. So the operations exist in practice and have never been written down. CATIO is behind its own reference implementations on its own vocabulary — the inverse of the usual drift, and the kind of gap nobody finds because nobody reads a table looking for what is absent.

### An export currently empties the trash

Soft delete is a project-level MUST across this family, and in a storage-tier deployment — admitted by [CA-022](../decisions/CA-022.md) Call 1, ruled STORAGE by the Director — the artifact *is* the store. A round-trip through the format therefore does not merely lose a flag; **it permanently empties the trash.** At L1 this is unavoidable today, because the file is the only store there is.

### Edges are deleted independently of things

A value detached from a field leaves the thing alive, the value alive, and the *relationship between them* in the trash. Thingalog carries `deleted_at` on its `:VALUE` relationships throughout (`graph.py:7226`), with repeat-detach guarded on `WHERE r.deleted_at IS NULL` (`:7240`), so a detached-then-restored attribution is ordinary recoverable state rather than an edge case.

A thing-only tombstone member would be internally inconsistent on the day it shipped, for exactly the reason this proposal exists.

## Proposed change

### 1. Two operations added to CATIO's write-operation table

| Operation | Description | REST | MCP Tool |
|-----------|-------------|------|----------|
| `detach_value` | Soft-delete the attachment of an enumerated value to a thing. The thing and the value both survive; the relationship is trashed. | `DELETE /api/items/{id}/fields/{label}/values/{value}` | `detach_value` |
| `detach_media` | Soft-delete the attachment of a photo to a thing. | `DELETE /api/items/{id}/photos/{photo}` | `detach_photo` |

Both are soft deletes, matching `remove_thing`. Repeat application is a no-op, per CATIO Design Principle 3.

### 2. `data.tombstones` — a new optional member

```jsonc
"data": {
  "items":  [ /* live things only */ ],
  "values": { /* unchanged */ },

  "tombstones": {
    "things": [
      {
        "template": "Artifact",
        "fields": { "Title": "Duplicate ledger scan", "Accession Number": "RHS.2019.013" },
        "deleted_at": "2026-03-04T11:22:00Z"
      }
    ],
    "edges": [
      {
        "template": "Artifact",
        "match": { "Accession Number": "RHS.2019.008" },
        "field": "Materials",
        "value": "Brass",
        "deleted_at": "2026-05-11T09:03:00Z"
      }
    ]
  }
}
```

**`tombstones.things[]`** carries the **whole thing**, in the same shape it would have in `data.items`, plus `deleted_at`.

**`tombstones.edges[]`** carries a reference to a thing that is still live, plus the field and value whose attachment was removed.

Identity in `match` follows CATIO §Identity and Deduplication unchanged: a field marked `unique: true` if the template has one, otherwise `Title` within the same template. **No new identity mechanism is introduced.**

### 3. The writer rule that makes the shape safe

> A writer MUST NOT include a tombstoned thing in `data.items`. A tombstoned thing appears in `data.tombstones.things` and nowhere else.

### 4. Reader behaviour

- A reader that does not recognise `data.tombstones` **MUST** ignore it, per the existing unknown-member rule. It then renders live things only — correct, not degraded.
- A 1.5 reader **MUST NOT** render a tombstoned thing as live, and **MUST NOT** apply a tombstoned edge.
- A tombstone whose `match` resolves to no thing in the document **MUST** be preserved on re-export and **MUST NOT** be an error. Partial exports make this reachable immediately.
- `deleted_at` is informational. A reader **MUST NOT** make rendering conditional on its value, so that a document with clock skew or a missing timestamp still behaves deterministically.

## Backward compatibility

**Additive and safe in both directions, which is the whole reason for the shape.**

| | |
|---|---|
| Existing 1.x catdefs | Remain valid. The member is optional and its absence means "no tombstones recorded," not "nothing was ever deleted." |
| **Old reader, new document** | Ignores `data.tombstones` wholesale and renders live things only. **This is the direction that matters**, and it works only because of the writer rule in §3. |
| New reader, old document | No member, nothing to apply. |
| Round-trip | A 1.4 reader that re-exports a 1.5 document **will drop the tombstones**, because it never saw them. That is data loss and it is unavoidable for any additive member; it is called out rather than hidden. |

### Why the obvious shape was rejected

A `deleted_at` on the item inside `data.items` is what most stores reach for first, because that is where the column already lives. **It is unsafe here.** A 1.4 reader ignores the unknown *key*, keeps the item, and renders deleted things as live — it resurrects the trash, silently, on every deployed reader. The separate member is ignored *wholesale*, so the failure mode is omission rather than resurrection.

This is the same hazard found twice elsewhere in this spec's 1.5 work: the danger is never what the new reader does, it is what the **old** reader does with new data, and the safe shape is always the one where the new thing is invisible rather than misread.

### The derivation that fixes the content of a tombstone

The separate-member constraint and soft-delete's recoverability together **force** the tombstone to carry the thing's full payload rather than a reference to it:

1. Soft delete means the data is recoverable, so the data must survive the round-trip.
2. The writer rule forbids the thing appearing in `data.items`.
3. Therefore the only place the data can survive is inside the tombstone.

A tombstone is a **relocated thing**, not a marker pointing at one. Edges differ because the thing they reference is still live and still carries its own data.

## Conformance tests

New category `conformance/tombstones/`.

| ID | Asserts |
|---|---|
| `ft-tomb-01` | A document with no `data.tombstones` is valid and unchanged in behaviour. |
| `ft-tomb-02` | A reader ignoring `data.tombstones` renders exactly the live things — the 1.4-degradation case. |
| `ft-tomb-03` | **GATING.** A writer that emits a tombstoned thing in *both* `data.items` and `data.tombstones.things` is non-conformant. This is the rule that prevents resurrection and it is a writer-side MUST. |
| `ft-tomb-04` | A 1.5 reader does not render a tombstoned thing as live. |
| `ft-tomb-05` | A 1.5 reader does not apply a tombstoned edge; the thing and the value both still exist. |
| `ft-tomb-06` | A tombstone whose `match` resolves to nothing is preserved on re-export and raises no error. |
| `ft-tomb-07` | Round-trip: a document with tombstones re-exports with every tombstone intact, including `deleted_at`. |
| `ft-tomb-08` | `detach_value` applied twice is a no-op (Principle 3). |
| `ft-tomb-09` | A tombstone with no `deleted_at` behaves identically to one with it. |

**Fixtures needed:** a catalog with one tombstoned thing, one tombstoned edge, one orphan tombstone, and a negative fixture for `ft-tomb-03`. The canonical reference file is not extended — tombstones in the flagship catalog would misrepresent it as having a trash.

**Per the ratified [CA-021](../decisions/CA-021.md) Call 1**, these tests drive the shipped implementation and are seen failing before the fix. Note the refinement at the same decision: where the fix introduces the symbol, the first red is vacuous and the mutation sweep carries the burden.

## Alternatives considered

**A flag inside `data.items`.** Rejected — resurrects the trash on every 1.4 reader. See above.

**The extension namespace, `x.<domain>.tombstones`.** Rejected for core, and the reasoning is worth keeping because it is the inverse of the usual answer. Two conformant runtimes would disagree about whether a trashed thing exists, which is the interoperability failure the namespace is meant to avoid creating. **But it is the right instrument for the prototype**, precisely because the concept has already been accepted into core and its shape already fixed: the prefix carries only the name, migration is a rename, and 1.4 readers degrade correctly in the meantime.

**A companion file or sidecar.** Rejected under value #7 — one file, complete product.

**Doing nothing and treating removal as out of scope.** This is the honest alternative and it fails on its own terms: the spec already specifies `remove_thing`. Declining to serialize it would mean deliberately keeping an operation whose outcome cannot be written down.

**Tombstoning by reference rather than by payload.** Rejected by the derivation above — the data would have nowhere to live.

## Open questions

1. **One collection with a discriminator, or two (`things` / `edges`)?** Drafted as two, because their identity shapes genuinely differ and a reader that cares only about things can ignore `edges` wholesale. A discriminator forces every reader to branch. **Flagged for the prototype.**
2. **What identifies a tombstoned edge when its value is later merged or renamed?** `match` + `field` + `value` is content-based, so a value rename orphans the tombstone. The orphan rule in §4 makes that safe rather than erroneous, but whether it is *correct* is unknown. **The prototype should exercise it.**
3. **Identity reuse.** Identity is content-based, so tombstoning a thing by `Title` and later creating a new thing with the same `Title` produces a collision. Does the new thing resurrect, or does the tombstone suppress it? **This is the sharpest unanswered question in the proposal** and it has no good answer without a stable id — which catdef deliberately does not have.
4. **Is `deleted_at` normative?** Drafted as informational. If anything is ever permitted to rely on it, conformance must say so.
5. **Does `detach_media` need its own tombstone shape?** Photos are deduplicated by filename rather than being enumerated values, so an `edges` entry keyed on `field`/`value` may not fit. Possibly a third collection, possibly a variant. **Deliberately unresolved** — no adopter has asked, and inventing it now would be the error this spec keeps catching.
6. **Does `remove_thing`'s existing wording need amending** to say that its outcome is serialized here, or is the cross-reference enough?

## Status of the prototype requirement

`CONTRIBUTING.md` §3 is **not satisfied.** Thingalog has accepted the prototype work as a by-product of TAL-1596 and will build to this shape under `x.thingalog.*`. This proposal should not merge before that exists and reports back, and questions 1–3 above are the ones the prototype is best placed to answer.
