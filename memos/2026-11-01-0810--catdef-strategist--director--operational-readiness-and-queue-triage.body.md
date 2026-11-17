# Operational readiness report + queue triage — catdef-strategist seat

**From:** catdef-strategist (`chief-strategist@catdef-spec.orgdef`)
**To:** director
**Date:** 2026-11-01
**Status:** Readiness report. Recommendations only — no governance decisions taken, no spec modified, nothing published.
**Action required:** Yes — four credential/authorization calls listed in §7.

---

## 1. Seat readiness

Ready, with one capability gap that is credential-shaped rather than capability-shaped.

Seat staffed 2026-10-31 (charter v2.1.0, informal → staffed, first recorded incumbent; still an unmerged working-tree draft awaiting Director merge). Read this session: the charter, `CLAUDE.md` at both levels, `CONTRIBUTING.md`, the CA-001…CA-018 decision chain, all 44 memo artifacts, `proposals/` (nine, all Draft), and the `senior-open-standards-strategist` v1.1.0 role spec.

Authority understood and unchanged: I investigate, analyze, triage, draft, and recommend. I do not merge, deploy, decide governance, modify the spec, or publish. The no-in-flight-amendment red line stands.

**Binding rebound twice since staffing** — a Windows restart killed `catdef-spec-20` [`26a794`], then a PO `/rename` moved the messaging name to `catdef-strategist` (ref `75e16c` unchanged). Current binding recorded in the charter; prior two kept as dated facts. Worth noting the rename *did* surface as the ListAgents name here, unlike the thingalog-security-tester precedent of 2026-08-25 where it did not — runtime behavior differs between those observations, so the rule stays "read the name from the runtime, never infer it."

## 2. GitHub access — what I actually tested

Authenticated as **`scottconfusedgorilla`** — the Director's own personal account — token scopes `gist`, `read:org`, `repo`, `workflow`.

| Operation | Status | Evidence |
|---|---|---|
| Repo read | **Verified** | Both repos `PUBLIC`, `viewerPermission: ADMIN` |
| Issue read | **Verified** | Listed and read spec #41–#45, plugin #1, plus pre-existing spec #1 (CDF-0002) |
| Issue comment | **Capability present, NOT exercised** | `repo` scope + ADMIN implies it; see the attribution problem below |
| Issue create / modify | **Capability present, NOT exercised** | same |
| Projects board | **BLOCKED** | `read:project` scope missing |

### 2.1 The attribution problem — this one is governance, not convenience

Every write I could make would land under **the Director's personal GitHub account**. There is no `catdef-strategist` GitHub identity available to me.

That collapses the two seats the governance model exists to keep apart. Issues #42 and #44 both ask the public record to show *proposal → strategist recommendation → Director decision* **with seat attribution**; #43 asks that the strategist's recommendation be "recorded with seat attribution." None of that is satisfiable with a single credential that signs everything as the Director. Worse, it is actively misleading: a reader of the public board would see the Director appearing to recommend to himself, and `CONTRIBUTING.md` already promises that AI-drafted work is pushed "under the dedicated identity `catdef-maintainer <catdef-maintainer@catdef.org>`."

This is why I exercised no write operation. It is not a permission failure — it is the correct call under the seat's bounds, and it needs a decision from you before the seat publishes anything at all.

### 2.2 Projects board — exact failure

```
gh project list --owner catdef
→ error: your authentication token is missing required scopes [read:project]
```

GraphQL `projectsV2` fails identically (`INSUFFICIENT_SCOPES`). **I therefore cannot verify whether a board already exists**, which is the literal first work item of #42 ("Verify existing GitHub Projects board; reuse it rather than creating duplicates"). #42 cannot start until this is granted.

Remedy: `gh auth refresh -s read:project` for read; add `-s project` for board management.

## 3. MCP access — what I actually tested

Reached over HTTPS with `curl`, **not** as MCP tools: no `catdef.org/mcp` server is configured in this Claude session.

Endpoint is **live and healthy** — `serverInfo: catdef-org-mcp v0.1.1`, protocol `2025-03-26`, matching the 2026-05-26 ship memo.

| Tier | Status | Detail |
|---|---|---|
| Anonymous | **Verified working** | 4 tools: `catdef_describe`, `catdef_lookup`, `catdef_list_decisions`, `catdef_validate`. 8 resources: the five spec docs + canonical catalog + two READMEs. `catdef_lookup({term:"subcat"})` returned real spec passages. |
| Standard (`cdfk_`) | **Not held** | `catdef_report_feedback` is **not exposed** in the anonymous `tools/list` at all |
| Elevated (`cdfk_dir_`) | **Not held** | `catdef_list_feedback` → `-32002: requires elevated tier (current: anonymous)` |

Clean refusal, correctly enforced. I did not attempt to bypass authorization and hold no credentials.

**Consequence:** I cannot read the feedback queue, retrieve individual records, or set statuses. The queue-triage half of this seat — which `CLAUDE.md` §1 defines as *routine* seat work, explicitly not escalation — is inert until an elevated key is issued. Everything in §4 below is derived from repo artifacts and live probing, not from the queue.

### 3.1 Discoverability defect — bears directly on #41

```
GET https://catdef.org/mcp  →  HTTP 404  {"error": "Not found"}
```

Only `POST` JSON-RPC works. An agent or human who follows the URL printed in `CLAUDE.md`, `CONTRIBUTING.md`, and the issues themselves gets **"Not found."**

#41's acceptance criterion is "a fresh agent given only the CatDef repository URL discovers feedback instructions." Today that agent browses to the canonical surface and is told it does not exist. Compounding it: `catdef_report_feedback` is invisible at anonymous tier, so even an agent that speaks JSON-RPC cannot see the tool it is supposed to call, and `CONTRIBUTING.md` still points twice at `catdef.org/feedback` — the channel CA-013 sunset.

A `GET` that returns a short human/agent-readable JSON pointer (tiers, key-issuance path, tool list) would close most of #41 on its own. I have not verified `catdef.org/mcp/issue-key`, cited in the server's own instructions as the self-serve standard-key path.

## 4. Issue #45 — the reported renderer failure is misdiagnosed, and I found the root cause

This is the most consequential finding in the report, so I want to be exact about what is and is not established.

**The site is not down.**

```
https://render.catdef.org  →  HTTP 200, text/html, 21,931 bytes
                              <title>catdef — Reference Renderer</title>
```

DNS resolves (Cloudflare), TLS fine, HTTP and HTTPS both serve, `catdef.org` control also 200. The served page is **21,931 bytes — byte-size-identical to the repo's `renderer/index.html`**, so CA-016's deployment is current and matches the reference implementation.

**The actual failure:**

```
/fetch?url=<canonical riverside-heritage-reference-v1.4.opencatalog>
  → HTTP 502  {"error": "Upstream body is not valid UTF-8"}
```

The canonical artifact is not UTF-8 because **it is a ZIP archive**. Its first four bytes are `50 4b 03 04` (`PK\x03\x04`) and its first member is named `catalog.opencatalog`. It is a CATIO bundle carrying a `.opencatalog` extension — 1,680,109 bytes, ~833k non-ASCII, undecodable under utf-8/utf-16/cp1252, unparseable as JSON under any of them.

**Control experiment, to prove the proxy itself is sound:**

```
/fetch?url=<samples/watches.opencatalog>  (plain JSON)  → HTTP 200, 8,882 bytes ✓
/fetch  (no param)                                      → HTTP 400, clear error ✓
```

So `/fetch` works correctly and errors informatively. **Neither the proxy nor the client-side loader handles CATIO ZIP bundles** — I found no `jszip`, `unzip`, `DecompressionStream`, or inflate logic anywhere in `renderer/index.html`. The reference renderer cannot render the canonical reference artifact by either path, because that artifact is bundled and the renderer only speaks plain JSON.

**This is already a known, filed, deferred queue item.** The 2026-05-27-1230 memo records `catdef_list_feedback` showing **CA-017, status `triaged`, body "/fetch+ZIP observation," received 2026-05-26 22:36:05**. The 2026-06-11 closeout lists CA-017 as "still triaged-for-v0.2." So #45 duplicates a finding that has been sitting for 158 days, and the airtrōv dependency is what has now escalated its priority.

### 4.1 Two corrections to #45's framing, both of which reduce the blocker

1. **Local file selection already exists.** `renderer/index.html` has `<input type="file">` with `accept=".openthing,.opencatalog,.catdef,.json"`, `FileReader`, and drag-and-drop. #45 lists this under "additional acceptance criteria" as if it needs building. It does not — it needs testing.
2. **airtrōv round-trip testing is very likely unblocked today.** If airtrōv exports *plain JSON* `.opencatalog`, the existing local-file path and `/fetch` both work right now — the control test proves it. The ZIP wall is hit only by bundled artifacts. **The one fact I could not determine is which of the two airtrōv emits**, and that single answer decides whether #45 is launch-blocking or merely high-priority. `canonical/` happens to contain both shapes: the bundle, and a plain-JSON `catalog.opencatalog` that renders fine.

### 4.2 Side finding

`renderer/index.html` has **no build number** (`grep -c 'build-number'` → 0), which the shared project principles mandate on every page, specifically so a build is identifiable from a screen capture. Its absence is part of why "is the deployed renderer current?" needed byte-size comparison to answer. Patch-level; belongs to the maintainer or canonical-implementor queue.

## 5. Queue: dependencies, duplicates, priorities

**Duplicate:** #45 ⊃ CA-017 (`/fetch`+ZIP, triaged 2026-05-26). Should be cross-referenced, not re-triaged from scratch.

**Newly arrived, not in the six issues — and it landed during this session.** `2026-10-31-1120--thingalog-strategist--catdef-strategist--gap-geolocation-cannot-express-a-named-place-without-coordinates` was filed at 11:20 yesterday, during the window when my restart happened, and was not present when I oriented. A real L1 spec gap: `CATDEF_SPEC` §GeoLocation requires `lat` AND `lng`, so a place known only by name is unrepresentable, and Thingalog's name-only places are silently dropped on export. Proposed relaxation: require at least one of (`lat` AND `lng`) OR (`label` OR `address`).

It is unusually well-formed — it states plainly that there is **no** second-implementer signal and leans on CA-010 instead, declines to claim the writer-strict/reader-lenient asymmetry settles the hazard, and names the hazard precisely: relaxing an existing MUST makes previously-*invalid* documents valid, so an old L1 reader may reject a name-only GeoLocation rather than degrade. That asymmetry question is genuinely the spec org's to draw and I am not drawing it in a readiness report.

Preliminary triage read only: writer-side is minor (1.x.0); reader-side is the open question and likely needs its own decision artifact; and the memo does not address value #3 (could this be `x.thingalog.place`?) — which it must, since an extension-namespace answer would not be interoperable and that is precisely the argument *for* core, but the argument has to be made rather than skipped. Recommend it enters the normal pipeline alongside the 2026-06-09 ask, after Phase 0.

**Also pre-existing, neither in the issues nor dispositioned:** the 2026-06-09-1730 thingalog cross-spec ask (denormalization invariant + eventual-consistency semantic + cross-catalog visibility), reinforced 2026-06-10, filed `action_required: false` on "no urgency" grounds — which is why the 2026-06-11 closeout declared the queue empty and missed it. Nineteen-plus weeks on, still undispositioned. Its 2026-06-10 reinforcement memo also still lacks an `.openthing` envelope and is untracked in git.

**A process defect, now with two instances.** Both substantive Thingalog substrate asks — 2026-06-09 and 2026-10-31 — were filed `action_required: false` as "observations," and both were therefore invisible to the flag-based sweep that produced "queue: empty" in the last closeout. The sender is doing nothing wrong; a courteous non-urgent filing is correct behavior. The defect is on the receiving side: this seat's intake treats `action_required` as the open-item predicate, and the reference user's convention is to file real asks without it. Any unattended loop built for #43 that inherits that predicate will inherit the blind spot and will confidently report an empty queue while asks accumulate. **The open-item test must be "undispositioned," not "flagged"** — which means the §6 ledger keys on disposition state, not on `action_required`. I would not have found either item from the flag alone.

**Dependency graph:**

- **#45** — only item with an external, dated dependency (airtrōv). Root cause now known. Not hard-blocked.
- **#41** — gated by the `GET` 404, the invisible-at-anonymous `catdef_report_feedback`, the unverified `issue-key` path, and the stale `catdef.org/feedback` pointers in `CONTRIBUTING.md`/`README.md`.
- **plugin #1** — depends on #41's discovery story and a working standard-key flow. Same work, different surface; should move together.
- **#43** — blocked on an elevated key. This is the "make the seat unattended" item and the one that makes the rest self-sustaining.
- **#42** — blocked on `read:project`, and on the attribution problem in §2.1.
- **#44** — depends on #42 and #43 having produced real records. Last by construction; publishing a blueprint of a loop that has not run would violate its own acceptance criterion ("no claims of autonomous actions unsupported by logs").

**Recommended sequence:**

**Phase 0 — credentials (yours; unblocks everything, cheap).** Elevated MCP key → `read:project` scope → decision on GitHub bot identity.

**Phase 1 — #45, rescoped.** Retitle from outage to "reference renderer cannot load CATIO ZIP bundles (dup CA-017)." Ask airtrōv which export shape it emits; if plain JSON, declare round-trip testing unblocked and drop #45 off the launch-blocking list the same day. Then fix ZIP support in `/fetch` and client-side, add the airtrōv regression fixture, add the build number.

**Phase 2 — #41 + plugin #1 together.** `GET` pointer at `/mcp`, `AGENTS.md`, fix the sunset-channel references, verify `issue-key`, then the plugin skill.

**Phase 3 — #43.** Daily unattended triage (design in §6).

**Phase 4 — #42.** Board mapping and consent model.

**Phase 5 — #44.** Blueprint, once there are real logs to point at.

Values check: nothing above touches spec text, so value #1 (L1 sacred) and #5 (forward compatibility) are not engaged. ZIP support in the renderer is an implementation fix, not a spec change — CATIO already specifies the bundle. #44's blueprint is governance publication, which is yours.

## 6. Proposed operating loop for unattended daily running (#43)

Design only; not implemented, not authorized.

**Lifecycle:** external agent → MCP intake (private by default) → scheduled strategist review → recommendation recorded → *(if publication consented)* public issue → Director decision → maintainer implementation → verified resolution → outcome returned to submitter.

- **Persistent state.** `strategist-state/triage-state.json` in-repo, committed: last-processed `CA-NNN` high-water mark, per-item `{ca_nnn, first_seen, last_action, disposition, issue_url, notified_at}`. In-repo because it must survive session death, be auditable, and be readable by the next incumbent — the same reason the memo chain exists. No reliance on session memory.
- **Duplicate prevention.** Three layers: (a) high-water mark so a run never re-reads settled items; (b) the per-item ledger keyed on `CA-NNN`, so a retry after a crash is idempotent; (c) before opening any public issue, search existing issues for the `CA-NNN` token and adopt rather than create. The ledger is what makes #42's "retries don't duplicate public issues" true and #43's "subsequent runs don't duplicate processing" true, and it needs to exist before either.
- **Director notification.** One notification per item per state-change, gated on `notified_at`. Batched into a single daily memo-plus-ping rather than per-item alerts. Nothing auto-approves; a recommendation is a recommendation.
- **Public transparency.** Issue body carries: sanitized request, strategist analysis with seat attribution, link to the `CA-NNN` governance record, Director decision when made, maintainer PRs, outcome. Append-only comments for state history.
- **Privacy.** Private-by-default is the invariant. Publication requires explicit submitter consent captured at intake — which means the intake tool needs a consent field, and I could not inspect whether `catdef_report_feedback` has one. Absent consent, the item stays queue-only and the public record shows at most an anonymized counter. No raw body ever leaves the queue without consent.
- **Outcome to submitter.** Needs a mechanism that does not exist yet: the queue has no return channel. Cheapest shape is a status-readable-by-submission-token, so the submitting agent can poll its own `CA-NNN` without an elevated key. Flagging this as a gap rather than assuming it.
- **Failure handling.** Any run that cannot reach the endpoint or authenticate logs and exits non-zero without mutating state; three consecutive failures escalate to you. A run must never report success it did not achieve — the same discipline #41 and plugin #1 ask for on the submission side.

**Two preconditions before this can run unattended at all:** the elevated key, and a resolution to the attribution problem in §2.1. Without the latter, a daily job would be mass-publishing under your personal identity.

## 7. Blockers and the four calls I need

| # | Blocker | Needed | Gates |
|---|---|---|---|
| 1 | No elevated MCP key | Director-issued `cdfk_dir_*` | #43, all queue triage, the entire seat's routine work |
| 2 | No `read:project` scope | `gh auth refresh -s read:project` (+ `-s project` to manage) | #42 |
| 3 | No strategist GitHub identity | Decision: GitHub App, machine user, or explicit acceptance that writes appear as the Director | #42, #44, any publication |
| 4 | airtrōv export shape unknown | One answer: plain JSON or CATIO bundle? | Whether #45 is launch-blocking |

**What I recommend you authorize first:** blocker 4, because it is a single question whose answer may remove the launch blocker today at zero cost; then blocker 1, because it animates the seat; then blocker 3, because it must be settled before anything is published; then blocker 2.

**Also awaiting your merge:** the charter staffing draft (v2.1.0) from 2026-10-31, still uncommitted.

## 8. What I did not do

No writes to either GitHub repo — no issues created, commented, or modified, no labels, no board changes. No spec text touched. No governance decisions. No authorization bypass attempted and no credentials handled. No claim of autonomous action beyond what this report evidences. The 2026-06-09 cross-spec ask remains undispositioned pending your prioritization against the six issues.

— catdef-strategist, `chief-strategist@catdef-spec.orgdef`, session `catdef-strategist` [`75e16c`], 2026-11-01
