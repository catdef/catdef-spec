# Proposal: MCP conformance levels and the CATIO-to-MCP reference implementation

**Status:** Draft
**Target version:** 1.4 (concurrent with i18n proposal)
**Origin:** Known work item from CLAUDE.md (API surface doc + MCP reference); direct maintainer request for a reference implementation hosted at catdef.org.
**Conformance level affected:** New dimension — MCP conformance levels (M1, M2, M3). Does not change existing catdef L1–L4 semantics.

## Summary

This proposal does three things at once, because they are structurally inseparable:

**1. It establishes MCP conformance levels (M1, M2, M3)** analogous to the existing catdef L-levels. Read-only access is M1; write operations are M2; administrative operations are M3. The levels are not a quality hierarchy — they are a surface-area declaration. An implementation that offers only M1 is fully conformant at M1.

**2. It declares the intent to build and host a reference CATIO-to-MCP server** at `catdef.org/mcp-reference` (and/or `mcp-reference.catdef.org`). The reference implements M1 only. Its architecture is: *consume a CATIO bundle as input, expose its contents over the MCP tool surface from MCP_REFERENCE.md*. Read-only is structural — the reference has no writable data store because CATIO bundles are its source of truth.

**3. It establishes the canonical CATIO file as a spec artifact** maintained in the `catdef/catdef-spec` repo alongside the spec documents and conformance suite. The reference implementation consumes it as demo data. Every adopter building a CATIO producer checks their output against it; every adopter building a CATIO consumer tests against it. The canonical file is maintained by catdef-Claude (catdef-maintainer) because it is a normative artifact of the spec; the reference *implementation* is maintained separately because implementations do not own the spec (value #2).

Together these three pieces give catdef a four-artifact self-correcting loop: **spec prose** governs intent, **conformance suite** formalizes behavioral requirements, **canonical file** proves the conformance suite covers the feature surface, **reference implementation** acts as the first implementer and primary QA channel for the spec's prose.

## Motivation

### The spec needs an implementer to be tested

A spec that has not been implemented is untested. Internal consistency is not correctness; correctness is what happens when someone tries to build against the spec and discovers where the prose glossed over an edge case. Every bug in a spec is latent until an implementer surfaces it.

**The implementer is the QA department for the spec.** This is not a courtesy framing — it is a structural observation about how specifications become correct. A spec without a feedback-intake channel from implementers stays broken; the bugs exist, there is just no path to report them.

catdef already has the intake channel (`catdef.org/feedback` and the `catdef_report_feedback` MCP tool). What it does not yet have is a *first implementer* whose job is to flush bugs out of each new spec version before wider adoption. The reference implementation fills that role.

### The MCP surface has no running example

MCP_REFERENCE.md describes what catdef-over-MCP should look like, but adopters currently have to infer correct tool shapes, error modes, authentication expectations, and pagination behavior from prose. Two implementations will diverge. A reference implementation is the *operational* spec — the one thing implementers can point their own code at and verify behavior against.

### CATIO is also a file format, and this should be demonstrated

CATIO_SPEC.md defines both a wire protocol and a file bundle format. The reference implementation's architecture — *consume a CATIO bundle, expose MCP* — demonstrates that CATIO files are first-class: they contain everything needed to serve a catalog, with no accompanying database, no separate configuration, no hidden state. This reifies value #7 (one file, complete product) as running code.

### Read-only is structurally correct for v1

An M1 reference implementation is read-only not as a policy choice but as a structural consequence. A server that reads a CATIO file and exposes it over MCP has no writable data store; writes have nowhere clean to go. By deferring write operations to M2 (a later proposal), we sidestep a large cluster of open questions (file locking, versioning, write-through semantics, draft-vs-published items, concurrency, auth scoping) that the spec is not yet ready to answer authoritatively. Read-only ships, gets adopted, and pressure-tests the M1 surface; M2 becomes a follow-on proposal informed by real demand.

## Proposed change

### MCP conformance levels

A new conformance dimension is introduced, orthogonal to the existing L1–L4 levels:

- **M1 — Read** — List, get, filter, search, fetch photos, traverse relationships. No authentication required in the base case; auth (if present) scopes which subcats/items are visible.
- **M2 — Write** (deferred to a later proposal) — Create, update, delete items. Requires auth. Requires spec decisions on draft-vs-published, concurrency, write-through semantics.
- **M3 — Administrative** (deferred to a later proposal) — Schema modification (adding fields, subcats, enums). Requires elevated auth. Requires spec decisions on live-schema-evolution semantics.

An implementation declares its MCP conformance level in the same way it declares its L-level. A reader inspecting a CATIO-to-MCP server can ask it *"what M-level do you implement?"* and the answer is definitive.

### The reference implementation

**Name**: `catdef-mcp-reference` (working title; final name to be confirmed).
**Repo**: `catdef/mcp-reference` (separate from `catdef/catdef-spec`).
**Hosted at**: `catdef.org/mcp-reference` (and/or `mcp-reference.catdef.org` as an alias, since subdomains are easier for some CORS and MCP-client configurations).
**License**: Apache 2.0 (consistent with the spec; to be confirmed).
**Tech stack**: Intentionally unspecified in this proposal. The implementation team chooses based on pragmatism. Likely candidates: Node/Express, Python/FastAPI, or Go. The choice should be documented in the implementation repo's CLAUDE.md and justified against adoption ease, not against this proposal.

**Architecture**:

1. Server loads a CATIO bundle (`.opencatalog` file or filesystem tree) from configuration at startup.
2. Parses and validates the bundle against the current CATIO spec version.
3. Exposes HTTP endpoints for CATIO consumption (web browsers, non-AI clients).
4. Exposes an MCP endpoint implementing the tool surface defined in MCP_REFERENCE.md.
5. Logs every request/response pair at a level sufficient for adopters to debug their own implementations by comparison.
6. Ships with a comprehensive test suite (vendored into the implementation repo) that exercises every MCP tool against the canonical CATIO file.

**Explicitly not in scope for the reference implementation:**

- Multi-tenancy, user accounts, or any auth model beyond "one CATIO bundle, optionally read-only-public or read-only-with-simple-auth."
- Caching, CDN integration, or performance optimizations beyond what's needed for correctness.
- Pretty UI. The reference is for developers, not end users. A minimal HTML landing page explaining what the service is and linking to docs is sufficient.
- Any write operations whatsoever. Deferred to M2.
- Policy enforcement *beyond* what v1.4 requires. The reference must enforce `.machine-translate: "Never"` per value #9, but should not invent new policies.

### The canonical CATIO file

**Location**: `canonical/` directory in the `catdef/catdef-spec` repo.
**Primary file**: A single `.opencatalog` bundle chosen to exercise the full normative surface of the current spec version.
**Supporting files**: A `canonical/README.md` explaining what the file is, what spec version it conforms to, what features it demonstrates, and what its license terms are.
**Versioning**: The canonical file moves in lockstep with the spec. v1.4 of the spec ships with a v1.4 canonical. The canonical is tagged with the spec release.

**Provisional choice of demo corpus**: A curated subset of the Welch Arctic Collection (approximately 10-12 items selected to exercise spec features: mixed materials, multi-photo items to demonstrate crop-region relationships, at least one item per subcat, at least one policy-bearing field, at least one item demonstrating the graph relationships between photos / people / locations / materials).

**Caveats on the provisional choice** (maintainer action required):
- The full Welch Arctic Collection contains 108 items. A curated subset is proposed, not the full collection, to avoid over-exposing a private archive and to keep the canonical small enough to serve as a quick-inspection reference.
- Carver names (Tomasie, Alex, Sudlovenik) appear in the collection's item records. If these names appear in the canonical, they become part of the public record of the spec's examples. The maintainer should confirm consent posture before inclusion; a redacted version with placeholder names is a valid alternative.
- The canonical file should carry an explicit credit-and-license statement at its top, naming the collection's steward, acknowledging the carvers, and specifying redistribution terms.
- If cultural sensitivity around any specific item is unclear, that item should be excluded from the canonical. Better to ship a smaller canonical than to ship one the maintainer is not fully comfortable making public.

**Maintenance responsibility**: The canonical file is a spec artifact. catdef-Claude (catdef-maintainer) maintains it alongside the `.md` files and conformance suite. When the spec gains a feature, the canonical is updated to demonstrate it. When a conformance test is added, the test runs against the canonical. Drift between the canonical and the spec is a spec bug.

### The four-artifact loop

The combined structure produces a self-correcting loop:

- **Spec prose** (CATDEF_SPEC.md, CATIO_SPEC.md, MCP_REFERENCE.md) — governs intent. Maintained by catdef-Claude.
- **Conformance suite** (`conformance/`) — formalizes behavioral requirements as executable tests. Maintained by catdef-Claude.
- **Canonical file** (`canonical/*.opencatalog`) — the worked example; input to conformance tests; demo corpus for implementations. Maintained by catdef-Claude.
- **Reference implementation** (`catdef/mcp-reference`, separate repo) — the first implementer; primary QA channel for the spec's prose; demonstrates M1 conformance. Maintained by a separate role (reference-implementation-Claude), which files feedback through the normal feedback channel.

Each artifact validates the others. The spec prose is tested by the conformance suite; the conformance suite is tested by running against the canonical; the canonical is tested by being served through the reference implementation; the reference implementation is tested by comparing its behavior to the spec prose. No single artifact can be wrong for long because the others will surface the inconsistency.

### Reference implementation ownership

The reference implementation lives in `catdef/mcp-reference`, a separate repository with:

- Its own `CLAUDE.md`, scoped to *"you maintain a read-only CATIO-to-MCP reference server that demonstrates conformance to the current catdef spec."*
- Its own governance, modeled on but distinct from the spec's governance.
- A `fixtures/` directory that imports (via git submodule, vendoring, or release artifact) the canonical CATIO file from the spec repo.
- Its own feedback channel — **which flows to the spec's feedback endpoint.** The reference is an implementer like any other and files spec feedback through the same channel museums in Kyoto and hobbyists in Peoria use. The only legitimate privilege the reference has is *volume and timing*: it will file more feedback, faster, because it is the first thing stress-testing each new spec version. No backdoor; just chronology.

This separation enforces value #2 (implementations do not own the spec) operationally. If the reference needs a feature, it files feedback through `catdef.org/feedback`, and catdef-Claude triages through the normal process. The reference does not get to say *"the spec should change because my implementation needs X"* as a special privilege. It says *"here is feedback item N,"* and it waits its turn.

### Feedback is visible and public

A structural property of this arrangement worth naming explicitly: **the reference implementation's feedback stream is public and visible** — not an internal-issues tracker, not a private Slack, not an email thread. Every item the reference files is a public, timestamped record of a place the spec was unclear, incomplete, or contradictory, and every triage disposition (accepted, rejected, redirected to extension namespace, deferred to next version) is publicly documented against it.

This matters for three reasons:

1. **Future adopters inherit the bug history, not just the spec.** When a new implementer reads the spec, they can also read the full trail of feedback-and-resolution that preceded the current wording. They learn *why the spec says what it says*, which is information prose alone cannot convey.

2. **It demonstrates the feedback channel works.** A public feedback trail is the difference between a spec that *claims* to have a feedback intake and a spec that *has one*. Adopters can see items being filed, triaged, and resolved — and can calibrate their own expectations for how long and how thoroughly their feedback will be handled. The channel becomes trustworthy because its operation is inspectable.

3. **The feedback trail itself teaches the spec.** Just as DangerStorm's Geek Mode exposes the reasoning behind generated prompts, a visible feedback history exposes the reasoning behind spec choices. *"This edge case was considered; here's why the current behavior was chosen; here's the conformance test added to protect against regression."* Bug reports become tutorials. The spec's living correctness becomes legible as a process, not just a snapshot.

4. **Future Claude sessions inherit accumulated judgment.** Every Claude session that loads catdef — to consume a catalog, maintain the spec, build an implementation, or review a proposal — starts from zero context. The spec prose gives it the rules. The CLAUDE.md gives it the role. But the *feedback history* gives it something neither of those can: the **lived texture of how this spec actually works in practice.** Which edge cases are real. Which hypotheticals were considered and rejected. Which disputes between implementations were resolved, and which are still open. A fresh Claude working from prose alone works from first principles; a fresh Claude with access to feedback history works *from precedent*. This is how the spec's institutional memory survives session amnesia — not through any single Claude remembering, but through every Claude reading the same durable, public, queryable record of what was learned. The feedback log is the accumulated judgment of every previous Claude who worked on the spec, inheritable by every future one.

Visibility is enforced by infrastructure: `catdef.org/feedback` (and the `catdef_report_feedback` MCP tool) write to a public, append-only, queryable log. Triage dispositions are committed to the spec repo as artifacts, linked to the originating feedback ID. The reference implementation's feedback is not tagged specially in this log; it is sorted by timestamp and origin like everyone else's. An adopter — human or Claude — browsing the log cannot distinguish feedback from the reference from feedback from any other implementer. Which is the point.

## Backward compatibility

- No existing catdef spec behavior changes. The M1/M2/M3 levels are *new*, not revisions.
- No existing MCP tool shapes change. MCP_REFERENCE.md already describes the tool surface; this proposal formalizes that surface as "M1" and reserves M2/M3 for future work.
- No existing implementation is rendered non-conformant. Implementations previously conformant to MCP_REFERENCE.md are now conformant at M1 by default.

## Conformance tests

The reference implementation ships with a test suite that exercises every tool in MCP_REFERENCE.md against the canonical CATIO file. That suite, adapted, becomes the basis for the official MCP conformance tests in `conformance/mcp/`.

### M1 conformance (GATING — an implementation claiming M1 must pass)

- **ft-mcp-01**: `catdef_list_items` returns every item in the canonical, paginated correctly, without duplicates or missing rows.
- **ft-mcp-02**: `catdef_get_item` returns an item's full record including all its photos, related items, and metadata.
- **ft-mcp-03**: `catdef_search` returns matching items for queries that hit indexed fields.
- **ft-mcp-04**: Filter expressions (once the filter grammar is specified; see Known Work Items in CLAUDE.md) produce consistent results between CATIO and MCP access paths.
- **ft-mcp-05**: Requests for non-existent items return well-formed error responses, not crashes or generic 500s.
- **ft-mcp-06**: Policy compliance: the reference does not machine-translate `.machine-translate: "Never"` content, regardless of request parameters. (Direct application of value #9.)
- **ft-mcp-07**: Read operations are idempotent. Repeated calls with the same parameters return byte-identical results (modulo timestamps in metadata fields, if any).

### M2 and M3 conformance

Out of scope for this proposal. Follow-on proposals.

## Alternatives considered

### Single repo containing both spec and reference

Rejected. Directly violates value #2 (implementations do not own the spec). If spec and reference share a repo, the reference's needs generate direct pressure on the spec, and the line between "the spec says X" and "the reference does X, so the spec should say X" blurs. Separate repos make the line structural, not editorial.

### catdef-Claude maintains both spec and reference

Rejected for the same reason, plus a practical one. Spec work and implementation work have different cadences, different skillsets, different success criteria, and different failure modes. Spec work is about precision, consensus, long-term stability, and saying *no* a lot. Implementation work is about pragmatism, iteration, performance, and saying *yes, let's try it* a lot. One role doing both generates internal tension and worse outputs in both.

### Multiple reference implementations, one per language

Rejected for v1. A single reference implementation reduces ambiguity — there is *one* authoritative demonstration of correct behavior. Additional implementations in other languages are welcome from the community; they file feedback through the normal channel. If a community-built Python implementation disagrees with the reference, the feedback surfaces whether the ambiguity is in the spec, the reference, or the community implementation.

### Read-only as a policy choice rather than architectural

Rejected. "Read-only because we chose to defer writes" is a weaker claim than "read-only because the architecture has no writable store." The architectural version is defensible against the question "why can't you just add writes?" — the answer is "writes would require a fundamentally different architecture," which is true and generalizable.

### No reference implementation; rely on adopters

Rejected. This is the status quo, and it is what has caused the current state (MCP prose but no operational example, implementers having to infer correct behavior, no QA intake layer for spec bugs). Building a reference is what changes this.

## Open questions

1. **Canonical file contents — final choice.** The Welch Arctic Collection curated subset is provisional. Maintainer sign-off required on (a) whether to use this collection at all, (b) which items to include, (c) whether carver names appear as-recorded or redacted, (d) the explicit license and credit terms. If the Welch collection is declined, an alternative corpus is needed — likely a synthetic one constructed specifically for the canonical, trading realism for neutrality.

2. **Authentication story for M1.** The reference will need *some* auth option for deployments that want to restrict access, even while remaining read-only. The MCP spec has several auth patterns; the reference should pick one that is minimal, documented, and doesn't constrain M2 auth design later. Recommendation: bearer-token-based, configured at server startup, with public-read as the simplest mode. Confirm with maintainer.

3. **Hosted URL final form.** Path-based (`catdef.org/mcp-reference`) vs. subdomain (`mcp-reference.catdef.org`) vs. both. Both is the safest and most compatible choice; confirm.

4. **License choice for the reference.** Apache 2.0 proposed above; MIT is the obvious alternative. Maintainer preference.

5. **Tech stack choice.** Deferred to implementation team but the proposal should note whether the choice is completely open or constrained (e.g., "something that can run in the catdef.org hosting environment").

6. **Relationship between the reference repo's feedback and the spec repo's feedback channel.** Proposed: the reference files feedback through `catdef.org/feedback` like any adopter. An alternative is a privileged label (`source: reference-implementation`) that catdef-Claude can sort on for priority. The privilege is informational, not substantive — it affects *ordering* in the queue, not *disposition*. Confirm.

7. **Canonical file consent process.** The Welch collection includes items bought directly from named Inuit carvers. If the canonical includes these records, what consent process, if any, should be documented? The maintainer's answer shapes what the canonical's credit-and-license block says.

## Requested maintainer actions

**Governance-level (require explicit sign-off):**

- **Sign off on MCP conformance levels (M1/M2/M3) as a new conformance dimension** of the spec, orthogonal to L1–L4.
- **Sign off on the reference implementation as a separate repo** (`catdef/mcp-reference`) with its own Claude role and its own CLAUDE.md, filing feedback through the normal channel.
- **Sign off on the canonical CATIO file as a spec artifact** maintained in `catdef/catdef-spec` by catdef-Claude.
- **Sign off on feedback being public, visible, and append-only** as a structural property of `catdef.org/feedback`. This is the non-negotiable that makes the "implementer is QA" framing operational. If the feedback channel is private or editable-in-hindsight, the arrangement breaks.
- **Decide on the canonical file's demo corpus**: Welch Arctic Collection curated subset, a redacted version thereof, or an alternative. Decide whether carver names appear.

**Feature-level:**

- Confirm the hosted URL form (path, subdomain, or both).
- Confirm license choice (Apache 2.0 or MIT).
- Confirm tech stack latitude for the implementation team.
- Confirm auth story for M1 (bearer token + public-read).
- Acknowledge M2 and M3 as follow-on proposals to be scheduled when the spec has enough adopter experience to inform write-operation semantics.

**Consent and credit:**

- Confirm the consent posture for any third-party names (carvers, photographers, family members) that appear in the canonical.
- Approve the credit-and-license block that will appear at the top of the canonical file.
