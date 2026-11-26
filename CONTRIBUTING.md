# Contributing to catdef

catdef is an open standard for machine-enhanceable descriptors of real-world objects and catalogs. This document describes how changes to the specification are proposed, reviewed, and accepted.

## Governance

catdef is stewarded independently of any single implementation. The standard exists to enable interoperability between runtimes — browser-only L1 readers, lightweight L2 servers, full-graph L3 platforms, and L4 hosting platforms — not to codify any one product's schema.

**Implementations do not own the spec.** Thingalog, PXMemo, dangerstorm, partner-branded renderers, and any future catdef runtime are equal citizens from the spec's perspective. Each is a consumer. Each can propose changes. No one gets unilateral authorship.

**Maintenance and AI-Assisted Review**

The catdef specification is maintained by the catdef maintainers with AI-assisted review. Routine editorial work — drafting proposals, adding conformance tests, applying patch-level fixes, and responding to incoming feedback — is drafted by Claude sessions operating under the roles defined in CLAUDE.md. Three bot identities are ratified: `catdef-maintainer <catdef-maintainer@catdef.org>`, `catdef-strategist <catdef-strategist@catdef.org>`, and `canonical-implementor <canonical-implementor@catdef.org>`. Version bumps and governance decisions are made only by the human Director.

**How maintainer-side changes actually land today, stated plainly because the previous wording described a process that was not being followed.** None of the three bot identities has its own GitHub account yet ([#48](https://github.com/catdef/catdef-spec/issues/48)). They exist only as git commit authorship. Every push therefore goes out under the Director's account, which holds bypass on the protected-branch rules, so maintainer-side changes land on `main` by **direct push under explicit per-act Director authorization** — that authorization is the review, and GitHub records the bypass each time. This is a temporary consequence of the identity gap, not a preference.

**When #48 lands, this reverts:** the bot identities get their own accounts without bypass, maintainer-side changes go through pull requests like everyone else's, and this paragraph is restored to describing a PR-based review process. That restoration is tracked as an acceptance criterion on #48.

**None of this changes anything for outside contributors.** Contributions arrive as issues and pull requests, are reviewed, and are merged by the Director. That path is real and is described below.

Structured feedback is submitted through the `catdef_report_feedback` tool on the canonical AI-peer MCP surface at `catdef.org/mcp`. That is an MCP endpoint, not a web page — a browser GET currently returns 404, tracked at [#49](https://github.com/catdef/catdef-spec/issues/49). The human-readable trail — triage dispositions and resulting spec changes — lives in `decisions/` and the proposals directory, as the spec’s institutional memory, readable by any future maintainer, adopter, or AI session. The former [catdef.org/feedback](https://catdef.org/feedback) channel is sunset; no new CDF-NNNN identifiers are issued.

## The change-request process

Changes to the specification follow a structured process:

### 1. Propose

Open a GitHub issue or pull request describing:

- **What the change is** — new field type, new attribute, new conformance requirement, clarification, etc.
- **Why it's needed** — concrete use case, ideally with an implementation that would adopt it
- **How it affects existing catdefs** — backward compatibility, migration story, impact on v1.x readers
- **Which conformance level it targets** — L1 (universal), L2 (server), L3 (graph), L4 (platform)

### 2. Discuss

Proposals are discussed openly. Expect questions about:

- Is this a spec concern or an implementation detail? (Most things are implementation details.)
- Does this generalize beyond the proposing implementation?
- Can it be expressed via the existing [extension namespace](CATDEF_SPEC.md#extension-namespace) (`x.<domain>.<identifier>`) instead?
- Does it obligate runtimes to add significant complexity? (Raise the conformance bar.)

### 3. Prototype

For non-trivial changes, a prototype in at least one implementation is required before the change is merged into the main spec. The prototype proves the change is buildable and catches edge cases before they become spec text.

### 4. Merge

Changes are merged when:

- Prototype demonstrates feasibility
- Conformance tests (if applicable) are written and passing
- Documentation is complete — main spec + examples + changelog entry
- No unresolved blocking objections from maintainers

### 5. Version

- **Patch (1.x.y)** — documentation clarifications, no schema changes
- **Minor (1.x.0)** — new optional fields, new field types, new settings. Old catdefs remain valid. Old runtimes gracefully ignore new fields.
- **Major (x.0.0)** — breaking changes to required fields or semantics. Runtime MUST check major version before rendering.

Version bumps happen at the end of a release cycle, not per-change.

## What NOT to propose

- **Implementation-specific features.** "How Thingalog does X" belongs in Thingalog's codebase, not the spec. If every runtime would do it differently, it's not spec-worthy.
- **Features that belong in the extension namespace.** If your use case can be expressed via `x.<domain>.<field>`, use that. The extension namespace exists precisely so the core spec stays lean.
- **Wishlist items without a concrete use case.** "Wouldn't it be cool if..." without an implementation that would adopt it gets deferred.
- **Changes that break L1 conformance.** The browser-only minimal tier is sacred. If your change requires a server, it belongs at L2+.

## What SHOULD be proposed

- **Gaps discovered during implementation.** If a real runtime hits a case the spec doesn't cover, that's spec feedback.
- **Interoperability issues.** Two implementations reading the same catdef differently → spec ambiguity.
- **New field types with cross-implementation demand.** If three unrelated runtimes all invent the same extension, it's time to promote it. Demand from a [designated reference user](decisions/CA-010.md) also qualifies as cross-implementer demand for promotion-gating purposes — gap-proposals from the canonical reference file or a CA-NNN-designated reference user (currently Thingalog, per CA-010) can drive promotion without waiting for a second unrelated implementation to converge. Reference-user demand flows through the same proposal-and-decision pipeline as any other source.
- **Conformance test additions.** More tests = more interoperability confidence.
- **Clarifications, corrections, typos.** Always welcome.

## Conformance test suite

The test suite in [conformance/](conformance/) is the practical expression of the standard. A change to the spec that doesn't come with test coverage isn't really part of the spec. Contributions to the test suite are as valuable as contributions to the spec text.

**The test suite is the standard.**

## The reference renderer

The canonical L1 reference renderer lives at [renderer/](renderer/) — a single self-contained `index.html`. It is a reference artifact under the same governance as the spec text and the conformance suite: changes affecting L1 conformance behavior need a proposal artifact and test coverage. See [renderer/README.md](renderer/README.md).

**Merging a renderer change to `main` does not deploy it.** The hosted instance at [render.catdef.org](https://render.catdef.org) is served by runtime fetch from the **`release`** branch, not from `main`. Deployment is a separate, deliberate fast-forward of `release` to `main`.

So for a renderer contribution:

- Open your PR against `main` as usual. Nothing you push to a branch or land on `main` reaches production.
- `main` is canonical and may be ahead of what is live. `release` is what is live.
- Promotion to `release` is a maintainer act on its own clock, not an automatic consequence of your merge. A merged renderer fix is not yet a shipped renderer fix.

This arrangement exists because the earlier one pinned the hosted instance to `main` directly, making every push touching `renderer/` a production deploy with no staging step — a structural hazard that only procedural care was holding back. See [decisions/CA-019.md](decisions/CA-019.md), which amends [CA-016](decisions/CA-016.md) on that point.

## Implementer roles

If you're building a catdef runtime, you're welcome to:

- Propose changes through the process above
- Add conformance tests
- Publish a conformance report showing which tests your implementation passes
- List your runtime in the implementations directory

You are NOT welcome to:

- Extend the core spec unilaterally in your implementation (use the extension namespace)
- Claim "catdef compliant" if you don't pass the test suite
- Use the catdef name/branding for a fork

## License

catdef is MIT licensed. Build whatever you want. If it passes the tests, it's catdef.

## Contact

File issues and PRs on this repository. Structured feedback at [catdef.org/feedback](https://catdef.org/feedback).
