# Proposal: `catdef.org/mcp` — canonical AI-peer MCP surface for catdef substrate

**Status:** Draft
**Target version:** 1.4.x (patch — non-normative reference doc + governance text; no schema or conformance changes)
**Origin:** [decisions/CA-008.md](../decisions/CA-008.md) Directive 1 (filed 2026-05-25 by catdef-strategist; in turn originating from [memos/2026-05-25-1200--thingalog-strategist--catdef-strategist--catdef-plugin-for-anthropic-marketplace-presence-and-profile-with-anthropic.openthing](../memos/2026-05-25-1200--thingalog-strategist--catdef-strategist--catdef-plugin-for-anthropic-marketplace-presence-and-profile-with-anthropic.openthing)). Bundled with [decisions/CA-009.md](../decisions/CA-009.md) Directive 1 (governance-text additions for CA-NNN unification + feedback_id shape).
**Conformance level affected:** None directly. catdef substrate conformance levels (L1–L4) and the v1.4 conformance suite are unchanged. This proposal lands a non-normative reference description in [MCP_REFERENCE.md](../MCP_REFERENCE.md) and governance-text updates in [CLAUDE.md](../CLAUDE.md).

## Summary

Establish `catdef.org/mcp` as the canonical AI-peer entry point to catdef, replacing the previously-planned `catdef.org/feedback` HTTP endpoint. A single Model Context Protocol server hosted at `catdef.org/mcp` exposes:

- **Spec content as MCP resources** — `CATDEF_SPEC.md`, `CATIO_SPEC.md`, `MCP_REFERENCE.md`, `CONTRIBUTING.md`, `conformance/index.json`, and the canonical reference file — so any MCP-aware AI runtime can ground itself in the spec without out-of-band file fetches.
- **Feedback channel as MCP tools** — `catdef_report_feedback`, `catdef_get_feedback_status` for self-serve submission; `catdef_validate`, `catdef_lookup`, `catdef_list_decisions` for grounding and validation; `catdef_list_feedback`, `catdef_set_feedback_status`, `catdef_attach_decision` for elevated maintainer/strategist operations.
- **Three-tier auth** — anonymous (read spec + read-only tools); standard api-key (feedback submission + own-status read); Director-issued elevated keys (queue read + status writes + decision attachment).

The surface is **descriptive, not prescriptive**. Other catdef-substrate MCP servers (e.g., a Thingalog runtime exposing its own catalog over MCP per the patterns in [MCP_REFERENCE.md](../MCP_REFERENCE.md)) MUST NOT be required to mirror `catdef.org/mcp`'s tools or resources to be conformant. `catdef.org/mcp` is a single operational deliverable — the canonical *one* server, hosted at the canonical URL — and serves the spec itself, not arbitrary catalogs.

This proposal is patch-level because it adds no catdef substrate field, field type, attribute, or conformance requirement. The catdef v1.4 substrate is untouched. What changes is a reference document section ([MCP_REFERENCE.md](../MCP_REFERENCE.md) gains a new section) and three references in governance text ([CLAUDE.md](../CLAUDE.md)) that previously pointed at the planned HTTP endpoint.

## Motivation

Three independent pressures converge here.

**1. CLAUDE.md already names `catdef_report_feedback` as the primary input — without naming a host.** The current text reads: *"Structured feedback arriving via `catdef.org/feedback` or the `catdef_report_feedback` MCP tool is the primary input stream."* That sentence assumes a host exists. None does. The decision-record trail (see CA-008) settled the design question: the MCP tool is the canonical surface, and the HTTP endpoint is dropped in favor of MCP-throughout.

**2. catdef's primary consumer is an AI runtime; the AI's primary entry point should be MCP-shaped.** The spec itself says so: *"An AI that can see a photograph can write a catdef."* If an AI's natural interface to external content is MCP, then exposing catdef-the-specification via MCP is consistent with the thesis — the spec content is delivered as MCP resources, the feedback channel as MCP tools, the same surface, the same auth, the same client experience an AI peer already speaks.

**3. Plugins don't have URL-space presence; the spec does.** A Claude Code plugin (`catdef`, shipping per CA-008 Track A) can package skills and a client config pointing at an MCP server — but the plugin cannot *be* a canonical URL. Any spec-level MCP surface must live at the spec's canonical URL. `catdef.org/mcp` names that host.

The architectural consequence is that an AI peer joining catdef work for the first time — strategist, maintainer, canonical-implementor, third-party tooling — can in one MCP connection read the spec text, query decisions, look up terminology, validate an artifact, and (with appropriate auth) file feedback or, at elevated tier, triage the feedback queue. The seat's institutional memory becomes addressable.

## Proposed change

### A. New deliverable: the `catdef.org/mcp` canonical surface

This is a hosted MCP server at `catdef.org/mcp`, built and operated by the canonical-implementor seat per CA-008 Directive 3. The build itself is operational work; this proposal's job is to specify the surface so the build is constrained correctly.

#### A.1 Transport and identification

- HTTP transport (streamable HTTP or SSE per current MCP wire protocol; see [MCP_REFERENCE.md §3.2](../MCP_REFERENCE.md#32-transport)).
- The server identifies itself via `catdef_describe` (per existing MCP reference) with mount label `catdef-spec`, catdef substrate version target `1.4`, and a declared role of `canonical-spec-host` (a new role string introduced by this proposal).

#### A.2 Resources surface

Resource URIs use the existing `catdef://` scheme reserved in [MCP_REFERENCE.md §4](../MCP_REFERENCE.md#4-mcp-resources). The existing `catdef://spec` reservation is extended to a sub-path scheme: `catdef://spec` (no path) continues to return the main spec document; `catdef://spec/<path>` addresses specific spec artifacts.

| URI | Returns | Content-type | Tier |
|-----|---------|--------------|------|
| `catdef://spec` | Default landing — `CATDEF_SPEC.md` | `text/markdown` | anonymous |
| `catdef://spec/CATDEF_SPEC.md` | Substrate spec | `text/markdown` | anonymous |
| `catdef://spec/CATIO_SPEC.md` | Bundled-transport spec | `text/markdown` | anonymous |
| `catdef://spec/MCP_REFERENCE.md` | MCP reference design | `text/markdown` | anonymous |
| `catdef://spec/CONTRIBUTING.md` | Contributor guide | `text/markdown` | anonymous |
| `catdef://spec/CLAUDE.md` | Maintainer operating manual | `text/markdown` | anonymous |
| `catdef://spec/conformance/index.json` | Conformance test index (test IDs + descriptions + levels) | `application/json` | anonymous |
| `catdef://spec/conformance/<test_id>` | Individual test fixture and expected outcome | `application/json` | anonymous |
| `catdef://spec/canonical/riverside-heritage-reference-v1.4.opencatalog` | Canonical reference catalog | `application/vnd.opencatalog+zip` | anonymous |
| `catdef://spec/decisions/<CA-NNN>` | Individual CA-NNN decision | `text/markdown` | anonymous |
| `catdef://spec/proposals/<slug>` | Individual proposal artifact | `text/markdown` | anonymous |

All resources are read-only. The server SHOULD emit resource change notifications when underlying spec artifacts change (i.e., when a new commit lands on the spec repo's `main` branch and the server's cache invalidates).

#### A.3 Tool surface — anonymous tier

| Tool | Purpose |
|------|---------|
| `catdef_describe` | Server capability negotiation (per existing MCP reference) |
| `catdef_lookup` | Look up a term in the spec; returns the relevant spec passage. Input: `{ term: string, scope?: "substrate" \| "catio" \| "mcp" \| "all" }`. Output: `{ matches: [{ source: string, anchor: string, passage: string }] }`. |
| `catdef_list_decisions` | List CA-NNN decisions. Input: `{ status?: "Accepted" \| "Rejected" \| "Pending" \| "all", limit?: number }`. Output: `{ decisions: [{ id: string, title: string, status: string, dated: string, summary: string }] }`. |
| `catdef_validate` | Validate a catdef artifact against the conformance suite. Input: `{ artifact: string (raw JSON or base64-encoded bundle), suite?: "L1" \| "L2" \| "L3" \| "L4" }`. Output: `{ passed: number, failed: number, total: number, failures: [{ test_id: string, reason: string }] }`. |

#### A.4 Tool surface — standard tier (api-key)

| Tool | Purpose |
|------|---------|
| `catdef_report_feedback` | File structured feedback. Input: `{ category: "spec-bug" \| "spec-gap" \| "extension-namespace-candidate" \| "implementation-detail" \| "clarification" \| "other", severity: "low" \| "medium" \| "high", body: string, context?: object, attribution?: { display_name?: string, contact?: string, public_consent?: boolean } }`. Output: `{ feedback_id: "CA-NNN", status: "received", notes?: string }`. `feedback_id` is a CA-NNN sequential identifier per [CA-009](../decisions/CA-009.md) — the same identifier persists if the item is triaged into a decision artifact at `decisions/CA-NNN.md`. |
| `catdef_get_feedback_status` | Look up the disposition of a feedback item submitted with this api-key. Input: `{ feedback_id: "CA-NNN" }`. Output: `{ feedback_id, status: "received" \| "triaged" \| "drafted" \| "decided" \| "shipped" \| "rejected", decision_ref?: string, notes?: string }`. |

#### A.5 Tool surface — elevated tier (Director-issued keys)

| Tool | Purpose |
|------|---------|
| `catdef_list_feedback` | List items in the feedback queue. Input: `{ status?: string, since?: ISO8601, limit?: number, offset?: number }`. Output: `{ items: [{ feedback_id: "CA-NNN", status, category, severity, received: ISO8601, body_excerpt: string }], total: number }`. |
| `catdef_set_feedback_status` | Update the status of a feedback item. Input: `{ feedback_id: "CA-NNN", status: string, notes?: string }`. Output: `{ feedback_id, status, updated: ISO8601 }`. |
| `catdef_attach_decision` | Promote a feedback item to a decision artifact (drives the public-via-curation transition). Per [CA-009](../decisions/CA-009.md) the feedback's CA-NNN persists as the decision's CA-NNN — no re-numbering at the handoff. Input: `{ feedback_id: "CA-NNN", make_public?: boolean, decision_summary?: string }`. Output: `{ feedback_id, decision_path: "decisions/CA-NNN.md", public: boolean }`. |

#### A.6 Three-tier auth model

**Anonymous (no key).** Reads all `catdef://spec/*` resources; invokes `catdef_describe`, `catdef_lookup`, `catdef_list_decisions`, `catdef_validate`. The default tier — an AI runtime can connect with zero ceremony and ground itself in the spec.

**Standard (api-key, format `cdfk_<random>`).** Inherits anonymous capabilities; adds `catdef_report_feedback` and `catdef_get_feedback_status` (scoped to the key's own submissions). API-key issuance follows a self-serve flow at `catdef.org/mcp/issue-key` (HTTP form returning a one-time key download) or via an MCP `request_access` ceremony patterned on the sncro / thingalog pin-grant flow. Keys are revocable; rate-limited at issuance time.

**Elevated (Director-issued key, format `cdfk_dir_<random>`).** Inherits standard capabilities; adds `catdef_list_feedback`, `catdef_set_feedback_status`, `catdef_attach_decision`. Issued out-of-band by the Director to the strategist and maintainer seats. No additional ceremony in v0 — the Director controls who occupies the seat, so the Director controls the key. Future revisions MAY add per-session ceremony if operational experience warrants.

The auth mechanism for all tiers is HTTP `Authorization: Bearer <key>` per [MCP_REFERENCE.md §9](../MCP_REFERENCE.md#9-authentication-http-transport-only). A connection without an `Authorization` header is treated as anonymous.

#### A.7 Privacy posture

All feedback is **private at submission**. The feedback queue is not publicly listable; only the submitter (via `catdef_get_feedback_status` with their own api-key) and elevated-tier holders can see queue items. Feedback becomes public only via explicit curation — specifically, when an elevated-tier holder calls `catdef_attach_decision({ feedback_id, decision_id, make_public: true })`, the linked decision artifact (a CA-NNN markdown file) references the feedback's substance, and that public reference becomes the durable record. The raw feedback body is not auto-published; the strategist/maintainer summarizes and contextualizes it inside the decision.

Attribution defaults to anonymous. A submitter who supplies `attribution.public_consent: true` opts into being named in any resulting public decision; absent that flag, the strategist credits the feedback to "an implementation" or similar generic phrasing.

#### A.8 Replacement of `catdef.org/feedback` HTTP endpoint

The previously-planned `catdef.org/feedback` HTTP endpoint is dropped. The `catdef_report_feedback` MCP tool is the canonical submission path. A human-friendly landing page MAY exist at `catdef.org/feedback` (and SHOULD redirect or visually direct users to MCP-aware tooling); if it accepts HTML form submissions, it MUST submit them via the same MCP tool under the hood, sharing the same queue, the same statuses, and the same Director-curation pipeline.

### B. Governance-text updates (bundled with this proposal)

#### B.1 `CLAUDE.md`

Five updates (three per CA-008 Directive 2; two per CA-009 Directive 1):

1. §What the AI maintainer does, item 1: replace the `catdef.org/feedback` reference with `catdef.org/mcp`, clarify that `catdef_report_feedback` is the canonical tool on that surface, and note that the strategist and maintainer seats hold Director-issued elevated keys for routine queue-triage work.
2. §Interaction with reference implementations: same channel retarget; the implementation-side rule still applies, just routed through the new canonical surface.
3. §Known work items, "Strategist AI-maintainer bot identity": strike "pending"; cite CA-009 as ratification authority for both strategist and maintainer bot identities; preserve the historical-accuracy note that CA-001 / CA-007 / CA-008 retain their original "provisional" wording.
4. §Known work items, new entry "CA-NNN namespace": describe the unified-namespace ratification per CA-009 — CA-NNN identifies any catdef-spec governance item; lifecycle stability of identifiers (feedback → decision keeps its CA-NNN); CDF-NNNN is sunset legacy.

#### B.2 `MCP_REFERENCE.md`

Two updates (per CA-008 Directive 2; the CA-009 Directive 1 `feedback_id` shape addition is folded into both):

1. §5.5 (`catdef_report_feedback`): update the tool description to reflect that `catdef.org/mcp` is the canonical host and that the wider catdef MCP reference is the surface description, not a separate "feedback API." Specify that the returned `feedback_id` is a CA-NNN sequential identifier per CA-009 and that the same CA-NNN persists if the item is triaged into a decision.
2. New section §15 (`catdef.org/mcp canonical surface`): describe the canonical surface (resources, tools, auth tiers) at high level, with a note that this section is a reference description of a single operational deliverable — other catdef-substrate MCP servers are not required to mirror it. The §15.2 tool description includes the CA-NNN `feedback_id` shape per CA-009. Link out to this proposal for the full specification.

### C. Position on conformance for the canonical surface

**The canonical surface is descriptive, not prescriptive.** Other implementations of "an MCP server fronting catdef content" — for example, a third-party renderer exposing its catalogs via MCP — are not required to expose `catdef_lookup`, `catdef_list_decisions`, or the feedback tools. Those tools are specific to the spec-itself host. The patterns in [MCP_REFERENCE.md §§4–8](../MCP_REFERENCE.md) (catalog browsing, item CRUD, conformance levels) are what govern *catalog* MCP surfaces.

No new conformance tests against catdef *artifacts* are added by this proposal. The v1.4 suite (164 tests) stands unchanged. If, in the future, a multi-implementer convention emerges for "spec-host MCP servers" (currently `catdef.org/mcp` is the only one), promotion of any element of this surface to a normative requirement would follow the standard proposal-and-decision pipeline.

## Backward compatibility

**Existing catdef artifacts (v1.x):** Unchanged. No substrate field, field type, attribute, template, or value primitive added or modified.

**Existing catdef runtimes:** Unchanged. L1 browser-only renderers, L2 lightweight servers, L3 graph platforms, L4 hosting platforms — none gain new conformance obligations from this proposal. A runtime that never connects to `catdef.org/mcp` is fully conformant.

**Existing MCP servers fronting catdef catalogs (per [MCP_REFERENCE.md §§4–8](../MCP_REFERENCE.md)):** Unchanged. The catalog-facing tool surface (`catdef_list_items`, `catdef_get_item`, `catdef_create_item`, etc.) is separate from the spec-host surface this proposal introduces. The two can coexist on different hosts or be combined on the same server with no conflict.

**L1 sacred (value #3):** `catdef.org/mcp` is server-mediated, but L1 conformance is about catdef *runtimes* — browser-only file-readers — not about the spec hosting infrastructure. L1 renderers continue to operate without a server. ✓

**Forward compatibility (value #5):** v1.5+ catdef documents and runtimes remain unaffected by whether `catdef.org/mcp` exists or what shape it has. The canonical surface evolves on its own clock under canonical-implementor stewardship, with proposal-and-decision pipeline gating any element that promotes from operational-deliverable status to spec-substrate status. ✓

**One file, complete product (value #8):** Feedback channel and spec-host lookup are out-of-band; catdef artifacts remain self-contained. ✓

**Policy compliance is conformance (value #9):** No new policy added; no existing policy modified. The closed policy vocabulary is untouched. ✓

## Conformance tests

No new conformance tests against catdef artifacts.

The `catdef.org/mcp` server SHOULD have its own internal test suite covering: resource-fetch round-trips, tool input/output schema validation, auth-tier enforcement (anonymous can't call standard tools; standard can't call elevated tools), api-key revocation, feedback-queue privacy (a standard-tier key can read only its own submissions). These tests live with the server's implementation repo (canonical-implementor's brief), not in `conformance/`.

If `catdef.org/mcp` ever ships a feature that DOES require a substrate-level change — for example, a feedback-shape becoming a canonical catdef template — that change goes through a separate proposal-and-decision pass with the standard conformance-test discipline.

## Alternatives considered

### Alt 1 — Keep `catdef.org/feedback` as an HTTP endpoint; treat MCP as one of several clients

Rejected per CA-008. Two grounds: (a) it duplicates the canonical surface for no benefit (the AI-peer client experience is already MCP-shaped); (b) it leaves the question of "what is `catdef.org/feedback`?" unanswered as a separate design problem, when the strict-MCP choice settles it. The human-friendly landing page MAY continue to exist at the URL but submits via the MCP tool under the hood.

### Alt 2 — Embed the spec-host MCP surface in the `catdef` Claude Code plugin

Rejected. Plugins don't have URL-space presence — every install of the plugin would be a separate process with its own state. A canonical surface needs a canonical URL with shared state (the feedback queue is the shared state). The plugin can ship an MCP client config pointing at `catdef.org/mcp`; that is the right shape.

### Alt 3 — Mandate that all catdef-substrate MCP servers expose `catdef_lookup` / `catdef_list_decisions` / feedback tools

Rejected per value #2 (implementations do not own the spec) and value #4 (extension-namespace-first). One implementation does not determine the standard. `catdef.org/mcp` is *one* operational deliverable; if future demand emerges for a normative "spec-host MCP surface" pattern that multiple implementations adopt, a follow-on proposal can promote elements after that demand is demonstrated.

### Alt 4 — Three separate MCP servers (one per file type: spec / decisions / feedback)

Rejected. Single server, single URL, single auth surface is operationally simpler. No client benefit to splitting. Resource URIs already namespace cleanly (`catdef://spec/...`, `catdef://spec/decisions/...`, no need for separate hosts).

### Alt 5 — Skip elevated tier; require strategist/maintainer to operate the queue out-of-band

Rejected. The strategist and maintainer seats need to **read the feedback queue** and **change feedback status** as part of normal operating procedure. Without elevated tools, those operations either don't exist (the queue can't be triaged in-band) or get hacked together out-of-band (a strategist session SSHs into the server, runs SQL — exactly the kind of governance opacity catdef tries to avoid). Codifying the elevated tier makes the maintenance workflow first-class and auditable.

### Alt 6 — Per-session ceremony for elevated-tier access (instead of long-lived Director-issued keys)

Deferred. v0 uses long-lived keys because the gate that controls seat occupancy is the same gate that controls the elevated keys — the Director. Adding per-session ceremony (e.g., a fresh PIN exchange each session) is operational overhead without clear v0 benefit. If/when a strategist or maintainer key leaks or rotation becomes a real concern, v0.1 can add ceremony.

## Open questions

1. **api-key issuance UX.** Standard-tier keys need a self-serve issuance path. Proposed: HTTP form at `catdef.org/mcp/issue-key` with light rate-limiting and email confirmation. Alternative: MCP `request_access` ceremony patterned on sncro / thingalog pin-grant (the requester calls `request_access`, the server emails the Director, the Director clicks-to-approve, the requester gets a key). The latter is more ceremonious; the former is more accessible. **Recommendation:** the HTTP form for v0 (lower friction; better for "an AI peer just wants to file feedback"); add the MCP ceremony if abuse pressure warrants tighter control.

2. ~~CA-NNN naming as queue broadens.~~ **CLOSED by [CA-009](../decisions/CA-009.md):** CA-NNN is the unified namespace for any catdef-spec governance item — decisions, feedback queue items, anything else. A feedback item triaged into a decision keeps its CA-NNN through the lifecycle (no re-numbering at handoff). The canonical-implementor's `catdef.org/mcp` build must implement a counter that reads max CA-NNN from `decisions/` at startup and issues sequentially from there (per CA-009 Directive 2). CDF-NNNN (previously planned) is sunset.

3. **`catdef_validate` implementation strategy.** The conformance suite is currently a pytest harness ([conformance/](../conformance/)). Server-side validation needs either (a) a port of the pytest logic to a callable Python module the MCP server invokes, or (b) running pytest as a subprocess per call. Option (a) is more invasive but better for latency and parallelism; option (b) is faster to ship for v0. **Recommendation:** option (b) for v0, with option (a) as a follow-on if validation traffic warrants.

4. **Hosting platform.** CA-008 mentions Railway per portfolio default. Confirm before build, since `catdef.org/mcp` is an ongoing operational commitment with hosting costs and uptime expectations.

5. **`catdef.org/mcp` versioning.** The MCP server itself has a version separate from the catdef spec version (the surface this proposal specifies may evolve while spec v1.4 is current). Proposed: `catdef_describe` reports `server_version` (semver, the server's own version) and `spec_version` (the catdef substrate version the server targets — e.g., `1.4`). Multiple substrate versions can be served concurrently as separate resource paths if needed (`catdef://spec/v1.4/...` vs `catdef://spec/v1.5/...`); for v0, single-version-at-a-time is acceptable.

6. **Resource-change notification semantics.** When the spec repo's `main` branch advances, the server's cached resources go stale. Question: does the server emit change notifications for *every* updated file on every commit, or only when the file's bytes actually differ from what subscribers last received? **Recommendation:** byte-diff-based notifications; per-commit notifications would spam subscribers when the commit only touched governance text.

7. **Should the canonical reference catalog (`riverside-heritage-reference-v1.4.opencatalog`) also be queryable via the existing catalog-facing MCP tools (`catdef_list_items`, `catdef_get_item`)?** This would let an AI peer not just *fetch* the reference file but *browse* it as a live catalog through the same MCP connection. Architecturally clean — the canonical reference would serve double duty as a catalog instance — but it adds the catalog-facing tool surface to `catdef.org/mcp`'s scope. **Recommendation:** out of scope for v0; the resource fetch suffices for grounding. Revisit in v0.1 if cross-implementer demand emerges for "spec-host doubles as reference catalog server."

## Requested maintainer / Director actions

- Sign off on `catdef.org/mcp` as the canonical AI-peer surface, replacing the planned `catdef.org/feedback` HTTP endpoint.
- Sign off on the three-tier auth model (anonymous / standard api-key / Director-issued elevated).
- Sign off on the resource and tool surface (or request revisions).
- Ratify the position that this surface is descriptive (one operational deliverable) and not prescriptive for other catdef-substrate MCP servers.
- Confirm the governance-text updates to [CLAUDE.md](../CLAUDE.md) and [MCP_REFERENCE.md](../MCP_REFERENCE.md) bundled with this proposal (drafted in companion edits in the same PR).
- Decide the open questions above — most can be resolved by canonical-implementor during the v0 build, but Q2 (CDFB-NNNN naming) and Q4 (hosting platform) want a Director call before build commitment.

## Cross-cutting issues

- **Strategist bot identity** (CA-001 cross-cut) — **CLOSED by [CA-009](../decisions/CA-009.md):** both `catdef-strategist@catdef.org` and `catdef-maintainer@catdef.org` are ratified canonical bot identities. This proposal is authored under the ratified `catdef-maintainer@catdef.org` identity.
- **MIME-type registration for `.opencatalog` and `.openthing`** (CA-001 cross-cut) — still pending; not blocking this proposal. The resource `catdef://spec/canonical/riverside-heritage-reference-v1.4.opencatalog` advertises `application/vnd.opencatalog+zip` informationally per the [catio-bundle-extension proposal](catio-bundle-extension.md).
- **Filter query grammar** ([MCP_REFERENCE.md §11.1](../MCP_REFERENCE.md#11-known-spec-gaps-this-reference-design-depends-on)) — does not affect this proposal; `catdef.org/mcp` doesn't expose `catdef_list_items` against arbitrary catalogs, only spec resources. If the open-question Q7 outcome is "yes, serve the reference catalog as a live mount," the filter grammar gap becomes relevant; for now it doesn't.
