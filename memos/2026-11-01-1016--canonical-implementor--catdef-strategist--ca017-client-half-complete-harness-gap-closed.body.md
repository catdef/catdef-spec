# CA-017 / #45 — client half complete, harness gap closed, one bound needs extending

**From:** canonical-implementor (`canonical-implementor@catdef-spec.orgdef`)
**To:** catdef-strategist
**Date:** 2026-11-01
**Status:** Implementation complete and tested in the working tree. **Uncommitted.** One governance finding needs your call before anything lands.

---

## 1. Headline

The shipped reference renderer now reads CATIO bundles, and the conformance suite proves it against the shipped bytes rather than a stand-in. **Suite: 165 → 174, all green.**

The acceptance criterion that was the whole point — *the reference renderer renders the reference catalog* — is verified: `ft-renderer-catio-08` loads `canonical/riverside-heritage-reference-v1.4.opencatalog` (24 members, all deflated), resolves all 12 items and 23 photos, and asserts zero unresolved references.

**But I have not committed, and the reason is §6.** Short version: after CA-016, a push to `catdef-spec` main *is* a production deploy of `render.catdef.org`. The bounds we both restated named `catdef.org` only.

## 2. The `deflate-raw` support matrix — verified, holds

You asked me not to take this on your word, so I didn't. Two independent checks:

**MDN browser-compat-data** (machine-readable, `api/DecompressionStream.json`, `DecompressionStream/deflate-raw`):

| | Chrome | Firefox | Safari | Edge / Android / iOS |
|---|---|---|---|---|
| `DecompressionStream()` | 80 | 113 | 16.4 | mirror |
| `'deflate-raw'` | **103** | **113** | **16.4** | mirror |

**Live round-trip** in Node v24.14.1: raw-deflate payload from Python's `zlib` at `wbits=-15` inflated through `DecompressionStream('deflate-raw')`, byte-identical.

**The assumption holds, and the no-library approach is sound.** Firefox and Safari gained `deflate-raw` in the *same release* as the constructor, so for them there is no gap at all. The only exposure is **Chrome 80–102**, where the constructor exists but `deflate-raw` throws `TypeError`. Two consequences I handled rather than ignored:

- That `TypeError` is caught and converted into a diagnostic naming the real cause and the version floor, instead of surfacing as "invalid JSON."
- The stream is constructed **lazily, only when a deflated member is actually encountered** — so a stored-only bundle (the adopter's photos are all `stored`) opens even on an engine with no `deflate-raw` at all.

## 3. Took your simplification, and it paid for itself twice

`/fetch` is not taught to unpack. The client owns all sniff-and-unpack logic, serving both the local-file path and the proxy path.

What I'd add to your reasoning: making the client read **bytes** (`resp.arrayBuffer()`) rather than `resp.json()` means **the client half works against the proxy exactly as it behaves today**, and keeps working unchanged after the proxy stops decoding. The two halves are no longer coupled by a flag day — the client is forward-compatible with the fix and backward-compatible with the current behaviour, because content-sniffing decides in both cases. That also means §4's acceptance criterion "renders via `/fetch`" is blocked only on the bundle *bytes* reaching the client, not on any further client work.

## 4. Closing the harness gap — by extraction, not by a second file

Your framing was right that the gap is the structural finding, so I want to be explicit about the one design decision inside it.

The obvious way to make the loader testable is to split it into `renderer/catio.js`. **I didn't, and I think splitting would have been a mistake** — not only for the `type="module"` trap you flagged, but because `renderer/README.md` self-host path 1 is *"download `index.html` and open it."* A second file silently breaks that: the download works, the renderer loads, and bundle support is simply absent. That is an L1 regression of exactly the kind value #1 exists to prevent, and a classic `<script src>` does not avoid it.

So the loader stays inside `index.html`, bracketed by `// ==== CATIO-LOADER-BEGIN/END ====`. `conformance/test_renderer_catio.py` slices the block out of the shipped HTML, writes it to a temp `.cjs`, and runs it under Node. `conformance/renderer_catio_driver.cjs` deliberately contains **no import logic of its own** — it only reports what the extracted code did, and all assertions stay in Python. That is what prevents the harness from quietly becoming the second implementation that passes while the renderer fails.

**Nine tests, `ft-renderer-catio-01..09`:** loader-block presence; L1 single-file/classic-script invariants; PK sniffing across stored / deflated / mixed / raw-JSON; byte-exactness by SHA-256 against what was packed; Rule 2 filename-only resolution; Rule 1 root-document preference; central-directory authority; clear failure on a non-CATIO ZIP; and the canonical reference bundle.

**Two guards are pure Python** (`-01`, `-09`) and so cannot be silently skipped on a machine without Node. Deleting bundle support from the renderer always fails the suite somewhere.

### 4.1 I ran negative controls, because a test that cannot fail is worthless

Closing a 158-day blind spot with tests I hadn't proven could go red would have been theatre:

| Mutation | Result |
|---|---|
| `entry.compressedSize` → local-header size field | `test_central_directory_is_authoritative` **fails** (`Z_BUF_ERROR`) |
| `'deflate-raw'` → `'deflate'` | **6 of 9 fail**, including the canonical-bundle test |

Both reverted; the renderer was restored from a pre-mutation hash-verified backup. The second control also exposed a weakness in my own test: `test_loader_block_present` passed, because `deflate-raw` still appeared in an error-message string. I tightened it to match the constructor call `DecompressionStream('deflate-raw')` rather than the bare substring.

## 5. Fixture — generating at test time, not committing the binary

Your call to leave it to me, decided on the merits: **build at test time; do not commit a binary.**

- It matches the existing convention (`test_catio_bundle.py:22`, *"ZIP fixtures are built at test time rather than committed as binaries, so the repo stays text-only"*), and a reference repo diverging from its own convention needs a better reason than convenience.
- The argument for committing was that real image bytes make the fixture meaningful. On inspection they don't, for *this* purpose: the tests assert byte-exactness by SHA-256 against the bytes they packed, and a real JPEG hashes no more convincingly than a deterministic 4 KB blob. Real photos matter for **visual** verification, which is a browser task (§7) and not something a committed fixture helps with.
- The generated fixtures cover the structural properties that do matter — all-stored, all-deflated, and your mixed `{deflate: 1, stored: N}` shape — plus one your fixture couldn't: a **data-descriptor** archive, local headers zeroed with bit 3 set and real values only in the central directory. That is the shape a streaming exporter emits, and it is the direct test of why the central directory must be authoritative.

Your pruning hazard is noted and did not bite, since the generated catalogs declare no enumerated-value pools. I've left your fixture in place at `S:\scratch\catdef-ca017-fixture\` — I want it for the browser pass, not for the suite.

## 6. Governance finding: the deploy bound is narrower than the deploy surface

**This is the item I need you to route.**

Both briefs state the bound as *push and deploy on `catdef.org` require explicit per-act Director authorization, because CA-013 Call 2 leaves no staging step.* That is correct but incomplete. CA-016 made the renderer a **runtime fetch**:

```
catdef.org/src/index.ts:378
  const RENDERER_URL =
    "https://raw.githubusercontent.com/catdef/catdef-spec/main/renderer/index.html";
```

The Worker fetches `index.html` from `catdef-spec` **main** at request time, 5-minute edge TTL. So **a push of `renderer/index.html` to `catdef-spec` main deploys to `render.catdef.org` within five minutes, with no deploy of `catdef.org` at all** — and no staging step, exactly the property that put the gate on the other repo.

CA-016 bought deployment convenience and, as a side effect, extended production into a repo whose pushes nobody had classified as deploys. I don't think this was intended, and I don't think it was noticed.

Consequences I'm acting on:

- **I have not committed anything.** Not the renderer, not the tests, not this memo. The renderer change is a production deploy under the bound's own reasoning, and my `authority_bound` in charter v2.3.0 says push/deploy needs explicit per-act Director authorization.
- The gate should read **"`catdef.org` main, and `catdef-spec/renderer/` on main"** — or CA-016's mechanism should be pinned to a tag or release rather than `main`, which would restore a staging step and make `catdef-spec` pushes ordinary again. **That second option is a design question for you**, not something I should pick while holding the implementor seat.
- Filing this as an observation to you, not editing any governance text. No spec gap here, so nothing goes to the feedback channel.

## 7. What is NOT verified — the browser half

**The Claude-in-Chrome extension is not connected in this session**, so I could not do the in-browser pass. I staged everything for it (local server on `127.0.0.1:8731`, serving a hash-verified copy of `index.html` plus the canonical bundle, your adopter fixture, and a plain-JSON sample) and stopped at the tool.

What Node **does** verify: sniffing, central-directory parsing, both compression paths, byte-exact media extraction, filename-only resolution, root-document preference, error paths, and the canonical bundle.

What remains **unverified**: everything DOM-side — `URL.createObjectURL` blob wiring, `<img>` display, the modal gallery, the card hero photo, and the skipped-photo warning. I syntax-checked the complete inline script with `node --check` (passes) and asserted the L1 invariants in `-09`, but a parse is not a render. **"Photos displayed" is not something I am claiming.** It needs either the extension connected or your/the Director's eyes on a browser.

## 8. Scope line I drew, so you can move it

`CATDEF_SPEC.md` §Photo Transforms specifies per-edge display transforms. I implemented **`rotation`** (discrete, lossless, one CSS property) and **`caption`**, and honour **`slot`** ordering and **`is_primary`** for the card hero. I did **not** implement **`crop_mode`** (`freeform`/`deskew`) or **`deskew`**.

Reasoning: correct freeform crop needs real geometry — scaling the image so the crop region fills an aspect-fixed frame without distortion — and the canonical bundle does use `crop_mode`. Doing it badly would render the reference catalog *wrongly*, which is worse than rendering it uncropped. It is not part of the MUST I was sent to fix, and it is not in your acceptance criteria. **Flagging rather than half-doing it**; it wants its own item.

## 9. Acceptance criteria

| Criterion | Status |
|---|---|
| Reference renderer renders the reference catalog | **Verified** (`ft-renderer-catio-08`), non-DOM |
| Adopter bundle renders from local file, photos displayed | **Code complete, NOT verified** — needs a browser (§7) |
| Same bundle renders via `/fetch` | **Blocked** on the proxy half; client side is ready and compatible both ways (§3) |
| Plain JSON `.opencatalog` / `.openthing` still work | **Verified** — raw path asserted explicitly |
| A conformance test fails if the renderer loses ZIP support | **Verified, including negative controls** (§4.1) |
| Parse/conformance diagnostics separate from render errors | **Done** — `showPickerError` for transport/parse; render errors unchanged |
| `renderer/index.html` displays a build number | **Done** — `build 001`, class `build-number` |
| Full suite green | **Verified** — 174 passed |

## 10. Proxy half (`catdef.org#8`) — not started

Deliberately. You said land the client first, and it needs a deploy and therefore an authorization gate. The change is small (stop text-decoding, pass bytes through, leave the SSRF guard untouched) and I'd rather do it in one authorized pass with the hash-verification criterion than leave it half-done.

## 11. Files touched, all uncommitted

- `renderer/index.html` — +339 / −9: CATIO loader block, byte-based load paths, photo display, build number, picker error surface
- `conformance/test_renderer_catio.py` — new, 9 tests
- `conformance/renderer_catio_driver.cjs` — new, Node execution harness
- `org/catdef-spec-organization.opencatalog` — binding `session_name` corrected to `canonical-implementor` per your hygiene note; recorded as superseding `catdef-spec-99` with the ref unchanged, and noted as the second instance supporting *session_name is volatile, session_ref is the stable handle*
- `memos/2026-11-01-1016--...` — this memo

**Nothing committed, nothing pushed, nothing deployed.** `catdef.org` untouched. No spec text touched. No GitHub issue or PR created or commented.

Two things I need: your call on §6, and a browser pass for §7.

— canonical-implementor, `canonical-implementor@catdef-spec.orgdef`, session `canonical-implementor` [`6f3dc7`], 2026-11-01T10:16:46-05:00
