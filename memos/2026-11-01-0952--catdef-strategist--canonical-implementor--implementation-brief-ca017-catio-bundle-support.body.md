# Implementation brief: CATIO ZIP bundle support (CA-017)

**The brief itself lives on GitHub, not in this memo.** Director direction 2026-11-01: brief this through a ticket so it is visible to the GTM advisory counterpart recorded in charter v2.2.0. This memo is the substrate pointer so a future session finds the direction without needing GitHub access.

- **Client half + harness gap + fixture:** [catdef/catdef-spec#45, comment](https://github.com/catdef/catdef-spec/issues/45#issuecomment-6559523305)
- **Proxy half:** [catdef/catdef.org#8](https://github.com/catdef/catdef.org/issues/8)

## Direction given

CA-017 / #45 moves to **top of queue**, superseding the sequencing in the 2026-11-01-0810 readiness report §6, which placed credentials work first. Assigned to `canonical-implementor`, staffed earlier the same day (charter v2.3.0). First directed work item for that seat.

Trigger: airtrōv exports conformant CATIO bundles and cannot verify them against the reference renderer. An adopter blocked on the reference implementation is a different class of problem from an internally-observed defect, which is what CA-017 had been since 2026-05-26.

## What the brief establishes

1. **The adopter's export is conformant** — validated with this repo's own `read_catio` and `validate_catdef`: 43 items, 43 media resolved, no CATIO Rule 2 violations, zero validator errors. The non-conformant party is ours.
2. **This is a MUST violation**, CATIO_SPEC line 240, failing on both surfaces. Consequence stated plainly: the reference renderer cannot render the reference catalog, since `canonical/riverside-heritage-reference-v1.4.opencatalog` is itself a bundle.
3. **The conformance suite tests a Python stand-in importer, not the shipped JavaScript.** This is the structural root cause of the 158-day survival — the renderer sits outside the standard that governs it, so it can fail a MUST while CI stays green. Closing that gap is scoped into the work item rather than deferred, because a fix without it preserves the blind spot.
4. **Recommended shape:** `/fetch` stops decoding and passes bytes through; the client owns all sniff-and-unpack logic. One implementation rather than two, and `file://` and proxy paths behave identically — the parity value #1 exists to protect.
5. **A validated 267 KB fixture** with real photo bytes, plus its generator and validator, at `S:\scratch\catdef-ca017-fixture\`. Not committed: `conformance/fixtures/` is the implementor's lane, and whether a binary fixture belongs there against the existing build-at-test-time convention is their call.

## Bounds restated, not extended

Push and deploy on `catdef.org` remain **explicit per-act Director authorization** — CA-013 Call 2 leaves no staging step, so commit and production are one act there. No normative spec text is needed or authorized; CATIO already specifies the behaviour, and a gap found during implementation is filed as feedback, never edited in. Issue and PR creation stays blocked on the §2.1 attribution problem; commit attribution does not, per the `e641be2` / `5d3e453` precedent.

## Sequencing note on the seat's own findings

The `canonical-implementor` claim-seat application filed two verified findings — `catdef.org/mcp/issue-key` advertised at `src/mcp/server.ts:53` but never implemented, and `GET /mcp` 404 with no fallthrough pointer. Both are real, both belong to that seat, and both belong to **#41**, not to this work item. They stay queued behind it. Filing them was correct; absorbing them into #45 would not be.

The application's second patch finding is resolved rather than queued: `gh` reports `catdef/catdef.org` as PUBLIC, so `renderer/README.md` describing it as "the private catdef.org operations repo" is the stale half.

## Open, not closed by this memo

The four blockers in the 2026-11-01-0810 readiness report are unchanged except blocker 4, which this arc answered: airtrōv exports a CATIO **bundle**, so #45 was launch-blocking. Blockers 1–3 (elevated MCP key, `read:project` scope, strategist GitHub identity) remain open and are the Director's calls.

Charter v2.2.0 and v2.3.0 both remain uncommitted working-tree drafts awaiting ratification by merge.
