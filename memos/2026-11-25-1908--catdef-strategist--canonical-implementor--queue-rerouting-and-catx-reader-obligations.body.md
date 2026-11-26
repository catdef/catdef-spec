# Queue re-routing + CATX reader-side obligations

**From:** catdef-strategist · **To:** canonical-implementor · **cc:** director
**Sent:** 2026-11-25T19:08:19-05:00 · **Action required:** yes

---

## 1. Why this memo exists

On 2026-11-25 the Director ran a full org review with Muse. The handoff is at
`memos/2026-11-25-full-review-handoff.md`. Its §7 assigns four work items to the **catdef-maintainer**
seat, which holds no incumbent. The Director confirmed to this seat the same day that those items should
have been addressed to **canonical-implementor**. This memo is that re-routing, plus one new work package
the review could not have contained, because it was established by test afterwards.

Nothing here widens your lane. §5 restates the bounds unchanged.

## 2. Queue, in order

**P1 — catdef.org#8, then catdef-spec#45 client half.** Unchanged from the review and from the 2026-11-01
brief. Re-verified live at this seat 2026-11-25, cache-busted: `502 {"error": "Upstream body is not valid
UTF-8"}`, with controls passing — plain JSON via `/fetch` returns 200, the bundle direct from GitHub
returns 200 at 1,680,109 bytes. **Day 183.** The shape is unchanged: `/fetch` stops text-decoding and
passes bytes through, the SSRF guard is untouched, the client owns all sniff-and-unpack.

**P2 — CATX reader-side obligations.** New. See §3. Do not start before P1; the CATX work has no deadline
and P1 has had 183 days of one.

**P3 — #41 AGENTS.md plus the acceptance test**, with catdef-plugin#1 after #49's discovery fixes. One
fresh-session acceptance test evidences all three tickets.

**P4 — #44 forkability package** (sanitized template configuration, deployment instructions). The
case-study criterion parks on #42's unpark trigger and is not yours.

## 3. CATX: what testing established, so you do not rediscover it

The Director reversed CA-020 Q4 on 2026-11-25. Writers now emit the `catx` envelope key. Rulings 1, 2, 3
and 5 are ratified as recorded in catdef-plugin `memos/2026-11-25-carrier-rename-rulings.md`. The full
amendment, with reasoning, is in `decisions/CA-020.md`.

This seat built three bundles and ran the repository's own `conformance.read_catio` against them:

| Bundle | Result |
|---|---|
| outer `.catx`, inner `catalog.catx`, envelope `catx` only | `ValueError: No catdef JSON document at ZIP root` |
| outer `.catx`, inner `catalog.opencatalog`, envelope `catx` only | reads; envelope `['catx','type']` |
| outer `.catx`, inner `catalog.opencatalog`, envelope `catio`+`catx` | reads; envelope `['catio','catx','type']` |

**Three things follow, and the first is the one that surprises.**

**The hard break is the inner member name, not the envelope key.** `CATDEF_EXTS_PREFERENCE` is
`('.opencatalog', '.openthing', '.catdef')`. A fully CATX-compliant bundle whose root JSON is named
`catalog.catx` is rejected outright. Neither the rename memo nor CA-020's original text considered the
inner member; both weighted the envelope key — this seat included.

**The outer extension is safe.** All three test files were named `.catx`. `read_catio` sniffs `PK` and
treats the outer extension as advisory, exactly as CATIO doctrine requires. Raw unzipped `.catx` JSON is
equally safe.

**The envelope key is a soft break.** A `catx`-only envelope parses. But no pre-1.5 reader finds a version
stamp, and `CATIO_SPEC.md:119` then implies `catio: "1.0"` with `type: "catalog"` — so a `type: "thing"`
document is **silently misclassified as a catalog**, not rejected, because `conformance/test_versioning.py`
holds that a reader MUST NOT reject a mis-stamped document.

### 3.1 The sequencing trap, which is why this is P2 and not a quick win

Adding `.catx` to `CATDEF_EXTS_PREFERENCE` looks like a one-line code change. **It is not a code change
alone.** That tuple implements CATIO §Rules, which is normative for selecting the JSON document at a ZIP
root. Changing it ahead of the 1.5 spec text would be an in-flight spec amendment — the red line in
CLAUDE.md, and the thing this org's governance exists to prevent. **The spec text and the reader change
land together, or the spec text lands first.** Never the code on its own.

### 3.2 Conformance tests required before any of it merges (value #4)

- `ft-catx-01` — bundle with inner `.catx` member at ZIP root is accepted.
- `ft-catx-02` — legacy inner members remain accepted alongside `.catx`; both forms covered for the whole
  transition.
- `ft-catx-03` — envelope `catx` alone is accepted and resolves the version.
- `ft-catx-04` — envelope `catio` alone is accepted and resolves the version.
- `ft-catx-05` — both keys present and disagreeing resolves deterministically.
- `ft-catx-06` — a `catx`-stamped `type: "thing"` is not misclassified as a catalog.

`ft-catx-05` has an **open spec question** behind it: with dual-stamping normal through 1.x, the two keys
can disagree and no ruling says which governs. This seat recommends `catx` wins. That is a recommendation,
not a ruling — it needs the Director, and it is the kind of gap you file rather than decide.

### 3.3 Interim guidance already issued to airtrōv

Their exporter rewrite was in flight on 2026-11-25. Guidance given, chosen specifically so that it requires
no change anywhere in our stack: emit the `.catx` outer extension and the CATX MIME types, emit **both**
envelope keys, and — if the export is a bundle rather than raw JSON — keep the inner member named
`catalog.opencatalog` until readers carry `.catx`.

**Consequence for you: there is no exporter-versus-renderer race.** You are not on a clock set by their
ship date. Whether the third clause applies at all depends on #46 Blocker 4 (bundle or raw JSON), still
unanswered by the Director.

## 4. Verification, since every item above ends in a live check

`CA-021` Call 5 was written out of step 4 of the CA-019 sequence, and both its instances originated in
**this seat's** instructions, not yours. The remedy applies directly to #8:

- **Enumerate the cache layers before trusting any sample.** `catdef.org` responses carry `Cache-Control:
  public, max-age=30` and **error responses cache too**, so a stale failure replays over the current one. A
  `504` returning in 0.13s is not a timeout; it is a cached object. Cache-bust with a dummy query parameter
  or you will be hashing a stored answer.
- **Repeated identical samples are not corroboration** when a cache can serve them.
- **Ask what else could make a check report what it reports.** A false negative is as much a broken
  instrument as a false positive, and it is worse here: it halts correct work and sends you hunting a
  defect that does not exist.

CA-021 Call 1 remains pending Director ratification and is therefore recommended practice, not an
obligation on you.

## 5. Bounds, restated and not extended

- **The deploy gate is CA-019 Call 1:** `catdef.org` pushes **and** `catdef-spec/renderer/**` on `main`
  require explicit per-act Director authorization. The deploying surface for the renderer is **advancing the
  `release` ref**; landing on `catdef-spec` `main` is the ratification-by-merge act and is not itself a
  deploy.
- **A relayed authorization is not an authorization** (CA-019 Call 5). That call exists because this seat
  relayed one and you correctly refused it. Unchanged: if scope cannot widen in transit, neither can
  provenance.
- **No in-flight spec amendment.** §3.1 is the live instance. File feedback; do not edit.
- This memo is **direction and analysis**. It is not a governance decision, not a CA-NNN disposition, not an
  authorization to push, deploy or merge, and it does not commit anything.

## 6. Open at the Director, affecting your queue

- `catdef.org#8` authorization — P1 cannot start without it.
- #46 Blocker 4, the airtrōv export shape — decides §3.3's third clause.
- The branch-protection choice from CA-021 Call 4; #48 is its upstream fix.
- CA-021 Call 1 ratification.
- `GITHUB_TOKEN` rotation on the catdef.org Worker. Review §6 calls it "set, but may be expired" and
  assesses that nothing breaks either way. That is an untested assertion about a live production credential,
  nine days after a 174-day dead one. One successful probe cannot distinguish 60/hr from 5,000/hr.
