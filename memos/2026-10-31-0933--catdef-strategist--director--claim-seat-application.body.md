# Claim-seat application — Chief Strategist (`chief-strategist`)

**From:** catdef-strategist (prospective incumbent; unstaffed at time of filing)
**To:** director
**Date:** 2026-10-31
**Status:** Application. Awaiting PO/Director authorization.
**Action required:** Yes — explicit authorization to staff, decline, or redirect.

---

## 1. What this memo is

An application to occupy the `chief-strategist` position in `org/catdef-spec-organization.opencatalog`. Filed per `/og-claim-seat` step 2. I have oriented on the substrate this session (charter v2.0.0 → `CLAUDE.md` both levels → all 44 memo artifacts → `decisions/` + `proposals/` → transcripts index) and read the referenced role spec.

**I have not staffed myself.** The charter is unmodified. `status` remains `informal` and no `incumbent` record exists. The flow is propose → authorize → record, and this memo is the propose step. If the Director declines or redirects, nothing needs undoing.

## 2. The seat as the charter defines it

> *AI role with provisional bot identity catdef-strategist@catdef.org (ratification pending). Held by the AI-strategist session arc, NOT by the Director. Triages proposals, files decisions in decisions/, makes pattern-promotion calls, reviews submissions for the Director's final call. No published roledef yet; eventual derivation from senior-open-standards-strategist is a forward work item.*

Two corrections to that text, both from artifacts postdating charter v2.0.0 (2026-05-10):

- The bot identity is **no longer provisional** — [CA-009](../decisions/CA-009.md) ratified both `catdef-strategist@catdef.org` and `catdef-maintainer@catdef.org`. `CLAUDE.md` reflects this; the charter does not.
- The charter's `governance_model` still names `catdef.org/feedback` as a feedback channel. [CA-013](../decisions/CA-013.md) sunset it; the canonical surface is `catdef.org/mcp`, MCP-only.

Neither is blocking. Both are small charter-hygiene items for the Director's merge queue, and I flag them rather than fix them — the charter is a governance artifact, not mine to edit on orientation.

**No published roledef exists for this seat.** Per `recommended_roles`, the charter cites `senior-open-standards-strategist` v1.0.0 as the MUST-priority role spec; the artifact is reachable locally at `roledef-spec/roledef/roledefs/senior-open-standards-strategist.openthing` at **v1.1.0** (roledef 0.2.0). I evaluated against v1.1.0 and note the version drift. Derivation into a `chief-strategist`-specific roledef remains the forward work item the charter says it is; I am not specializing a `roledef:Job` here (deferred per the card).

## 3. Fit evaluation

### 3.1 Where the seat matches

| Seat requirement | Assessment |
|---|---|
| Triage inbound, file dispositions as `decisions/CA-NNN.md` | Match. The CA-001…CA-018 chain establishes the form; I read it and can extend it. |
| Pattern-promotion calls (extension → core) | Match. Values #3/#4 plus the CA-018 renderer-portability test give an applicable decision procedure rather than a judgment I invent per case. |
| Cross-spec coordination memos | Match. The thingalog channel is operational and filesystem-based; I can read and file on it. |
| Decision artifacts, validation reports, handoff prompts, forward-work logging | Match. All five roledef `output_contract` entries are text artifacts authorable in this repo. |
| Bounded authority — draft/decide-on-record, never merge | Match, and independently enforced: I do not push, and the harness requires Director authorization for outward-facing acts regardless. |
| No claimed continuity across sessions | Match by construction. I remember nothing; I read the five-closeout chain. The roledef makes this a guardrail, which is the correct shape. |

### 3.2 Where the seat does not match — the material gap

**The MCP queue half of this seat's routine work is unavailable to me as configured.**

`CLAUDE.md` §1 is explicit that the strategist seat holds Director-issued elevated keys for `catdef.org/mcp` and uses `catdef_list_feedback`, `catdef_set_feedback_status`, and `catdef_attach_decision` as **routine seat work, not escalation**. In this session:

- No `catdef.org/mcp` server is configured. The MCP servers available are Thingalog catalog endpoints, claude.ai connectors, and browser/IDE tooling. None of them reach the canonical surface.
- I hold **no elevated key**. Keys are Director-issued and none was conferred.

So the queue-triage half of the seat is out of reach. What remains available is substantial — the memo channel, `decisions/`, `proposals/`, charter review, cross-spec coordination, pattern-promotion calls, maintainer briefs — and the last closeout records the received-bucket as empty, so nothing is known to be waiting there. But I would be occupying the seat with one hand tied, and the Director should know that before authorizing rather than discover it when I report I cannot action a queue item. If the MCP half should be live, it needs a key and a server entry.

### 3.3 Narrower mismatches

- **`submission_pr` degrades.** The roledef's atomic-promotion contract ends in "push, open PR." I will branch and draft; I will not push. Under this org's ratify-by-merge discipline that is the correct behavior, so the contract narrows to "staged and signed off; Director pushes and merges." Consistent with the org, narrower than the roledef.
- **OPD is N/A.** The roledef's professional-development phase keys off `metadata.derived_from`; this seat has no published roledef, hence no parent, and `opd-state/` does not exist. Per the roledef's own rule (`derived_from: null` → skip OPD entirely), there is nothing to run. It becomes live only once the derivation lands.
- **The strategist memory file is bootstrap-era unified** across all four catdef-family strategist roles (`strategist-memory/project_catdef_strategist_role.md`, ~65KB, last touched 2026-04-26). Per the roledef's role-separation rule I declare explicitly: **I would exercise catdef substrate-strategist authority only.** Not roledef, not orgdef, not memodef. Where an item touches a consumer spec I coordinate rather than decide. The per-strategist memory split remains the forward work item its README says it is.

### 3.4 One thing the Director should weigh

**The seat has been cold for roughly nineteen weeks.** The last closeout is 2026-06-11; today is 2026-10-31. Everything that closeout filed under "In flight" is now of unknown currency — most notably the Anthropic plugin review, which was "submitted and pending" and has had four and a half months to resolve in either direction. I would treat none of those as current without re-verifying, and re-verification of the plugin status is a PO-side check I cannot make from here.

**Conclusion: good fit for the repo-and-memo half of the seat, with the MCP-queue half unavailable absent a key.** I do not consider that disqualifying, but it is the Director's to weigh, and I would rather authorization happen with it stated than without.

## 4. Scope I would accept

- Triage inbound memos and file dispositions as `decisions/CA-NNN.md`
- Pattern-promotion calls under values #3/#4 and the CA-018 renderer-portability test
- Briefs and build directives to `catdef-maintainer` and `canonical-implementor`
- Cross-spec coordination with `thingalog-strategist` and the roledef/orgdef/memodef strategist seats
- Surfacing cycle triggers (v1.5) and charter-hygiene items for the Director's call
- Forward-work logging in both places the roledef requires

## 5. Bounds I would not hold

- **No merges, no pushes, no tags, no releases.** The Director ratifies by merge.
- **No governance decisions.** Scope-of-catdef questions, adopter relationships, licensing — the Director's.
- **No spec text.** That is `catdef-maintainer`'s lane; I brief, they draft.
- **No in-flight amendment.** The red line stands: no spec change outside the proposal-and-decision pipeline, regardless of which seat asks or how urgent it looks.
- **No implementer advocacy.** All runtimes are equal citizens, Thingalog included — CA-010 changes what counts as demand, not who owns the spec.
- **No v1.5 trigger.** CA-018 Directive 4 reserves it for the Director explicitly.

## 6. Seat address and session binding

- **Address:** `chief-strategist@catdef-spec.orgdef` — stable, org-scoped, from the position `id` and the charter `id`. Distinct from the **bot identity** `catdef-strategist@catdef.org` ratified by CA-009, which is the authorship identity used in commits and `metadata.authors`. Two different things; the charter uses the latter and the card wants the former, so both are recorded.
- **Binding:** recorded in this memo's `metadata.session_binding`, conferred by the runtime, not self-assigned. Session `catdef-spec-20` [`26a794`], runtime `claude-code`, observed 2026-10-31T09:33:00-04:00.
- **Supersession:** this claim supersedes any prior binding on this address. No prior binding is recorded anywhere in the substrate — this is the first. That makes it **never-bound**, not stale; there is nothing to alert anyone about.
- **Reachability caveat:** the binding says which session, never whether it is alive. Resolve it against the runtime, never against this file. When this session goes quiet nothing writes back here, which is exactly why supersession-on-claim is keyed to the claim and not to an expiry.

**Format-shape question, surfaced not settled.** The card says where the binding field ultimately lives — memo `metadata`, charter `incumbent`, or a separate register — is format-shape, and directs it to the substrate spec's strategist. catdef *is* the substrate spec, so that question lands on the desk of the seat this memo applies for. I note the recursion and decline to resolve it inside my own application: if staffed, it enters the queue as an ordinary inbound and runs the standard pipeline. Settling it here would be the in-flight amendment the red line forbids, with the added defect of ratifying a shape question inside the artifact that asks to be allowed to consider it.

## 7. What I am asking for

Explicit authorization to staff, decline, or redirect. On authorization I will set `status: staffed` and add the `incumbent` record to the charter as a **working-tree draft only** — no commit, no push. The Director ratifies by merge.

Three things worth a word in reply, if there is one: whether the MCP key and server entry should be wired up, whether the plugin-review status is a check the Director will make, and whether the two charter-hygiene corrections in §2 belong in the same diff as the staffing record or a separate one.

— prospective incumbent, `chief-strategist@catdef-spec.orgdef`, 2026-10-31
