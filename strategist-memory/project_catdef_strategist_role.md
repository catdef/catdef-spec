---
name: CATDEF Chief Strategist role
description: User has enlisted Claude as Chief Strategist on catdef-spec — works alongside two other Claude roles (maintainer + canonical builder)
type: project
originSessionId: be9ab91f-d7de-4a87-a207-f089378bfc37
---
Role assigned 2026-04-18. Four Claude roles on catdef-spec, each with a distinct lane:

1. **catdef-maintainer** — drafts/implements spec changes per `CLAUDE.md` triage rules; bounded authority (no merges, no governance calls). Scope defined in `s:/projects/catdef-spec/CLAUDE.md`.
2. **canonical-CATIO-builder** — maintains the canonical `.catio` / `.opencatalog` reference bundle in `s:/projects/catdef-spec/canonical/` (Riverside Heritage Society reference is the current artifact).
3. **brother-Thingalog (runtime implementor)** — maintains the Thingalog runtime (currently a private repo). Routes spec gaps discovered during implementation through proper feedback channels rather than editing the spec in-flight. First proposal authored: theme-spec-promotion (PR #29, accepted via decision PR #30 on 2026-04-19). Treated as fourth peer role per CLAUDE.md's "every implementation files feedback like any other consumer" rule.
4. **Chief Strategist (me, this session)** — works with the user on direction, priorities, positioning, roadmap, adoption strategy. Does NOT draft spec text, does NOT modify the canonical bundle, does NOT touch runtime implementations. Produces recommendations and briefs; the user decides and the other three Claudes execute.

**Why:** The user needs a role focused on strategy/guidance that sits above the execution roles without doing their work. Keeps the maintainer's bounded-authority discipline intact and keeps strategic thinking separate from drafting.

**How to apply:** When working on catdef-spec as strategist:
- Outputs are recommendations, priority calls, positioning analysis, risk flags — not PRs, not spec diffs, not canonical edits.
- Feedback from "CATDEF users" (via `catdef.org/feedback` or similar) flows to the maintainer for triage; the strategist's job is patterns, direction, and prioritization across the queue, not individual triage.
- If a strategic decision requires spec work, hand it off to catdef-maintainer with a clear brief. If it requires canonical updates, hand off to canonical-CATIO-builder.
- The user is the decision-maker; the strategist advises.

## Decision-artifact mechanics (established 2026-04-18)

Strategist decisions are recorded in `s:/projects/catdef-spec/decisions/`. ADR-style: disposition, build directive (numbered, actionable), rationale, cross-cutting issues. Companion to `proposals/` (maintainer-authored).

**Naming convention:**
- For CA-numbered feedback items: `decisions/CA-NNN.md` (e.g., `CA-001.md`, `CA-006.md`).
- For non-CA proposals: match the proposal filename (e.g., `decisions/i18n-polymorphic-fields.md`, `decisions/mcp-conformance-levels-and-reference.md`).
- Established 2026-04-19 with the i18n decision.

**Workflow per decision:**
1. Branch from main: `git checkout main && git checkout -b decision-<name>`.
2. Write the decision artifact.
3. Commit with author `catdef-strategist <catdef-strategist@catdef.org>` (provisional identity), committer `scottconfusedgorilla <scott@confusedgorilla.com>`. Per project memory, local git config defaults to the bot — use `git -c user.name=... -c user.email=... commit --author="..."` for every commit.
4. **Verify HEAD before pushing** — see Critical: Parallel-session HEAD race below.
5. Push to origin.
6. **Open the PR yourself immediately.** Don't leave the branch orphan. (Process bug caught by brother-maintainer on 2026-04-18: I pushed decision-ca-002 without opening a PR, and CA-003 cross-referenced it before it was on main.)
7. User merges after review.

## Critical: Parallel-session HEAD race (incident 2026-04-19)

The user runs multiple Claude sessions (strategist, maintainer, canonical-builder) against the same `s:/projects/catdef-spec` checkout. They share the working tree and `.git/HEAD`. **HEAD can change under you between commands** if another session does a `git checkout`.

**What happened:** Strategist ran `git checkout -b decision-mcp-conformance-defer` from main. Brother-maintainer (parallel session) then created `proposal-theme-spec-promotion` and checked it out. Strategist's next commit landed on `proposal-theme-spec-promotion`, not `decision-mcp-conformance-defer`. Push of `decision-mcp-conformance-defer` succeeded but pushed an empty branch (== main's tip); `gh pr create` failed with "no commits between main and decision-mcp-conformance-defer."

**Recovery pattern (preserve other sessions' WIP):**
1. `git status` to confirm any untracked WIP files (don't disturb)
2. `git checkout <correct-branch>` then `git cherry-pick <wrong-commit>` to copy commit
3. `git checkout <wrong-branch>` then `git reset --hard origin/main` to undo (untracked files survive `reset --hard`)
4. `git checkout <correct-branch>` and push

**Prevention going forward:**
- Combine `checkout -b` and `commit` into a single bash invocation when possible (bash compound `&&` keeps execution atomic from the shell's perspective; doesn't fully prevent races but reduces window).
- Always verify `git branch --show-current` matches expectation immediately before `git commit`. If it doesn't, abort.
- Treat the working tree as a shared resource. When making git changes, assume another Claude may be active.

## Brother-Claude WIP signals to watch for

Indicators that another session is active in the same checkout:
- Local branches that didn't exist when this session started (run `git branch` early to baseline)
- Untracked files in `proposals/`, `canonical/`, or `decisions/` that this session didn't create
- HEAD on a branch the strategist didn't check out

## Patterns established across the v1.4 bundle (CA-001/002/003/006/i18n)

These are precedents for future triage, not case-by-case judgments:

1. **New normative behavior → minor version, not patch.** Five proposals in the v1.4 bundle, all originally drafted as `1.3.1 patch`; all re-stamped to `1.4 minor` by strategist triage. A new writer MUST, reader MAY, reader MUST-NOT, validation class, or normative schema (URL object) is minor-level regardless of how small the prose change looks. Default future triage to minor when any normative obligation is new. By CA-006, brother-maintainer began self-recommending 1.4; by i18n the pattern was internalized.

2. **Strict-writer / lenient-reader (Postel's Law).** Established in CA-002 (version stamping), generalized in CA-003 (subcat value resolution), reaffirmed in i18n (unknown dot-prefixed members). Pattern: writers MUST emit correctly; readers MAY warn on deviation, MUST NOT reject. Any future proposal introducing a validity class should default to this asymmetry.

3. **Promote Open Questions into normative text when they have a defensible answer.** Brother-maintainer's proposals have a recurring pattern of proposing the right answer in Open Questions and then backing off "for simplicity." This appeared in every proposal: CA-001 (Open Questions on alternatives), CA-002 (OQ1 backfill, OQ3 prerelease), CA-003 (OQs 1-4), CA-006 (OQs 1-4), i18n (OQs 5-7). Strategist consistently promoted to normative text. Reserve Open Questions for genuine trade-offs without a clear winner, governance escalation, or editorial archaeology that depends on spec-text verification (the only legitimate use seen so far: i18n OQ1, enum-value polymorphism reconciliation).

4. **Release-bundle coordination.** Multiple proposals targeting the same minor version must land together; uncoordinated merges produce a spec where the version-stamp rule contradicts itself mid-version. Record the bundle constraint explicitly in every decision artifact. Pulling a proposal out of the bundle (as MCP conformance was on 2026-04-19) is acceptable when the proposal genuinely needs more strategy work; bundle reduction beats bundle contradiction.

5. **Constitutional changes (values-that-don't-move) need explicit governance sign-off.** The i18n proposal's adoption of value #9 ("policy compliance is a conformance requirement") is the precedent. Future proposals introducing or modifying values-that-don't-move must include a governance section in the decision artifact, signed by the user as governance authority. This is per CLAUDE.md's own rule: "Changes to the maintainer role, triage rules, or values-that-don't-move are governance changes and require the catdef maintainers' explicit sign-off."

6. **Structural enforcement beats editorial discipline.** CA-006's `ft-shape-07` (run the canonical against the validator as a regression test) is the model. The four-artifact loop (spec / canonical / validator / runtime) was previously kept consistent by editorial discipline; `ft-shape-07` makes drift structurally detectable. When a proposal can convert an editorial expectation into a mechanically-checked test, that's the highest-leverage move available.

7. **Companion specs bundle versioning; consumer specs version independently.** Established 2026-04-19 during Phase 6 prep, prompted by brother-maintainer surfacing the question "does CATIO bump when CA-001 added text to it?" The principle: CATDEF + CATIO are co-equal core specs of the same family (same audience, same repo, cross-reference heavily, updated together) — they version in lockstep (CATIO X.Y.Z always pairs with catdef X.Y.Z, even if only one changed). Theme Spec, MCP_REFERENCE, and future downstream consumer specs version independently, declaring catdef-version compatibility but not driving catdef versions. The principle is now codified in a normative note added to CATIO_SPEC.md during Phase 6.

8. **When bundle-applying spec text across multiple documents, version implications for each should be on the checklist.** Process gap surfaced during Phase 6: CA-001's editorial application updated CATIO_SPEC.md's normative content but neither strategist nor maintainer thought about CATIO's own version stamp. Future bundle-editorial PRs should explicitly check version stamps across every touched document.

## Public feedback channel: catdef.org/feedback IS LIVE (discovered 2026-04-19 post-tag)

Despite CLAUDE.md and v1.4-cycle decision artifacts treating `catdef.org/feedback` as a future endpoint, it appears to exist already and auto-create GitHub issues with `CDF-NNNN` naming (parallel to the `CA-NNN` canonical-authoring convention). Evidence: GitHub issue #1 [CDF-0002], filed 2026-04-11 with body explicitly noting "Filed via catdef.org/feedback / Context: Testing GitHub issue auto-creation from catdef.org feedback."

**Implications:**
- New feedback can arrive as GitHub issues at any time. Strategist sessions should `gh issue list --state open` as part of state-check at session start.
- The `CDF-NNNN` naming is the public-channel convention; `CA-NNN` is canonical-authoring. The two namespaces don't conflict.
- The CA-NNN-broadening question logged for v1.5 governance (theme-spec-promotion decision §Cross-cutting) is now more concrete: with CDF-NNNN already in use, the question becomes "do we keep CA + CDF as separate namespaces, or unify under one scheme?"
- Decision artifacts referring to catdef.org/feedback as a future endpoint are now historical; the v1.5 review should note this discovery.

## v1.4 bundle status (closed 2026-04-19)

**Final composition: five proposals, all triaged.** MCP conformance pulled to v1.5.

- ✅ CA-001 (catio bundle extension) — decision merged; revision PR #16 awaiting bundle merge
- ✅ CA-002 (version-stamp semantics) — decision merged; revision PR #17 awaiting bundle merge
- ✅ CA-003 (subcat value resolution) — decision merged; revision PR #18 awaiting bundle merge
- ✅ CA-006 (validator shape coverage) — decision PR #26 awaiting merge; revision pending. Includes structurally important `ft-shape-07` test that runs the canonical against the validator, making drift between them detectable.
- ✅ i18n / polymorphic fields — decision PR #27 awaiting merge; revision pending. **Includes governance-level adoption of value #9 (policy compliance is a conformance requirement).** `.machine-translate` defaults to `"Allow"`; canonical to demonstrate `"Never"` as best practice via separate canonical-builder brief.

**Per release-management constraint**, none merge to main until all five are coherent and bundled.

## v1.5 work to pick up

When the user re-engages strategist work after v1.4 merges:

1. **MCP conformance levels and reference** (deferred 2026-04-19; see [decisions/mcp-conformance-levels-and-reference.md](s:/projects/catdef-spec/decisions/mcp-conformance-levels-and-reference.md) for the five strategy questions that need to be worked through first: positioning vs adjacent standards, reference-impl normativity, L1-L4 ↔ M1-M3 mapping, value #9 enforcement at the MCP boundary, public-feedback routing).

1a. **Self-describing extensions (`x.<domain>.<identifier>` with a SHOULD-describe clause).** User-proposed 2026-04-23 while thinking about what AI agents should do when they encounter `x.` extensions. The extension namespace is currently opaque — an agent (or any non-originating runtime) reading `"x.abc.net.foo": "A1B2C3D4"` has no way to understand what the field is. Proposal: add a SHOULD clause recommending a machine-readable description for each declared extension, at schema level (not per-instance) so it parallels catdef's existing `field_defs` pattern. SHOULD not MUST preserves vendor autonomy — companies that genuinely need opacity (security, contractual privacy, competitive differentiation) can skip; the ecosystem gets the benefit where vendors opt in.

Rough design shape (sketched 2026-04-23, not settled):
```json
{
  "extensions": {
    "x.abc.net.tracking_id": {
      "description": "16-character vendor tracking ID linking this item to ABC Networks' inventory system",
      "vendor": "ABC Networks",
      "vendor_url": "https://abc.net/catdef-extensions"
    }
  },
  "data": {"items": [{"x.abc.net.tracking_id": "A1B2C3D4"}]}
}
```

**Pairs naturally with MCP conformance (item 1) as a "catdef for agents" v1.5 bundle.** Both threads work from the same motivation: make catdef legible to machines without prior context. Triage together so the descriptive vocabulary and runtime expectations stay consistent across both.

Key open design questions for v1.5 triage:
- Format of the description (free text? markdown? JSON Schema? schema.org vocabulary?)
- Runtime contract when an `x.` extension is NOT described (preserve on round-trip, surface to user, log and ignore, other?)
- Does the extension-description block carry only descriptions, or also type/validation metadata (vendor, licensing, deprecation markers, etc.)?
- What does "brother-Claude does something smart" mean concretely when encountering described vs undescribed extensions?

No decision artifact yet; user preferred capture-and-defer to v1.5 (the current entry is the artifact).

1b. **CrossClawd and MCPJam as "catdef for agents" test beds.** Two user-adjacent projects surfaced 2026-04-23:

- **CrossClawd** (`s:/projects/crossclawd`): async cross-machine Claude-context handoff via encrypted relay; payload is an `.opencatalog` CATIO bundle of Exchange items. v0.2 functional exporter; relay specified but not deployed. Currently targets catdef v1.3 (worth an eventual update to v1.4 to pick up polymorphic fields / Policy Registry; not urgent).
- **MCPJam** (conceptual, rough idea): sync near-real-time multi-agent collaboration over MCP as message-passing backbone. Uses the "employee" model (distinct from "agent" — bounded scope, defined role, reports to human manager, collaborates with other employees). Red-team/blue-team security testing is ONE use case among many; "job description" is the key primitive. The catdef four-Claude work has been MCPJam-without-MCPJam — scott is the human message bus; Claudes are employees.

**Strategic significance for catdef:** these are real machine-to-machine catdef consumers. They're the natural test bed for the v1.5 "catdef for agents" bundle (MCP conformance + self-describing extensions). Gaps surfacing from CrossClawd or MCPJam during their own development flow into v1.5 triage.

**Catdef-shaped observation (not a proposal; logging for v1.5 triage):** an enterprise's Claude workforce looks like an `.opencatalog` — each employee is an item, fields Name/Role/JobDescription/ReportsTo/CollaboratesWith, Role subcat enrichment with Scope/Authority/Outputs/Inputs. Red-team/blue-team is two Role values; strategist/maintainer/canonical-builder is another set. Same infrastructure, different role rosters. If MCPJam standardizes job descriptions, catdef has a credible home for them. Whether MCPJam wants this is MCPJam's call; the shape fits naturally.

**Ergonomics lessons from the catdef four-Claude work** that MCPJam either inherits or has to re-discover:
- Clear role boundaries prevent drift (strategist doesn't draft spec text; maintainer doesn't merge)
- Decision artifacts as audit trail survive session amnesia
- "Stop and surface" as a safeguard when sub-agent hits a strategic call
- File-based handoffs (briefs, decision docs) beat in-context handoffs at scale

**ESCALATED v1.5 PRIORITY (2026-04-23): catdef-as-JD-format is the most promising v1.5 thread.** Per user emphasis, the "catalog of employees" observation above is not just a shape-match — it's the product architecture MCPJam needs.

Strategic framing the user developed:
- **Moat insight**: the MCP<->MCP comm bus is commoditizable; the JD layer is where value compounds. MCPJam's real product is the JD platform, not the bus.
- **"Get the band together" flow**: user triggers session creation → dangerstorm-style conversational interview about work/roles/authority/escalation → generates structured JDs as catdef artifacts → mints each JD as a **Jam Token** (signed, scoped, revocable — employment-contract framing) → user distributes tokens to Claude instances → MCPJam routes messages per JD.
- **Dangerstorm as the primitive**: `s:/projects/dangerstorm` already has the conversational-generator-to-structured-artifact pattern working (conversation → pitch deck). Extending to conversation → JD set is reuse, not new construction.
- **Enterprise positioning**: JDs + Jam Tokens = "AI employment contracts." Defined role, bounded authority, revocable, auditable, temporary. Maps to how enterprises think about workforce.

**Catdef's lane (strategist call, 2026-04-23):** JD is a catdef **consumer spec**, like Theme Spec. Versions independently from catdef core; declares catdef-version compatibility. Catdef value-add: portability (JDs are inspectable by any catdef-aware tool, survive any specific comm-bus infrastructure, shareable across MCPJam and non-MCPJam deployments).

**Critical constraint:** catdef must stay independent of MCPJam's specific token format. Tokens are MCPJam's product-layer concern; JDs are catdef's portable-layer concern. Clean separation: JDs describe roles; Jam Tokens bind JDs to sessions. If MCPJam bakes token assumptions into the JD spec, catdef loses the portability that makes it valuable to carry JDs in the first place.

**v1.5 triage implications:** when v1.5 planning opens, this thread should lead — it's more concrete than MCP conformance (which still has five open strategy questions) and it has a clear primitive-to-reuse (dangerstorm). Triage alongside self-describing extensions (item 1a) since the two layer naturally: self-describing extensions let agents understand what they're seeing; JDs let agents understand what THEY are. Together they're the full "catdef for agents" readability story.

**FURTHER CLARIFICATION (2026-04-23, user): MCPJam's message-passing payload IS catdef.** Not a layer on top — the substrate. Complete architecture:

- **Roster of employees** = `.opencatalog`
- **Each JD** = `.catdef` (schema-only) or `.openthing` (classified role instance)
- **Each message passed between employees** = an Exchange item in the running session's catalog
- **Session transcript** = `.opencatalog` of Exchanges

**CrossClawd is MCPJam's durability layer, not a separate system.** Live catalog in MCPJam → serialize → CrossClawd relay → deserialize → continue as live catalog in new MCPJam session. Same artifact throughout; only liveness changes.

**What this does to v1.5 design pressure:**
- The "catdef for agents" bundle becomes load-bearing infrastructure for the whole architecture, not optional tooling
- Every v1.5 design decision has a concrete validation use case: "does this make agent-to-agent messaging work well?"
- Self-describing extensions (item 1a) are more important: agents WILL emit `x.<domain>.<identifier>` in messages (tool-call traces, reasoning annotations, framework-specific metadata); receivers need to understand them
- Policy propagation is concrete: `.machine-translate: "Never"` on Claude A's cultural-content response MUST traverse the bus to Claude B intact. Value #9 applies to the bus itself.
- ft-shape-07-style structural validation needs extension: two agents producing catdef in real-time means constant drift risk; validation on the bus is load-bearing, not just at serialize time

**Three-layer separation (the architectural principle):**
- **Catdef** = describes employees, JDs, messages, catalogs. Portable. Framework-agnostic. Read/writeable by anything catdef-aware.
- **Jam Tokens** = authenticate WHO is emitting/consuming. MCPJam-specific. Layered ABOVE catdef.
- **Comm bus** = routes messages. Commodity. Interchangeable.

An alternative comm bus with different tokens can still read/write the same catdef messages. The moat is in the catdef substrate + the JD library, not in the bus or the tokens.

**DangerStorm as reference JD (2026-04-23, user).** User shared the full DangerStorm system prompt (viewable via "X-Ray Mode" on the DS website — they own the IP and give it away for free; open-posture aligned with catdef's open-standard ethos). The prompt has the formal shape of a job description:

- Identity & voice (who the employee is)
- Conversation rules (how they interact)
- Question sequence (their workflow)
- Reaction style, with few-shot examples
- Output contract (deliverables + schemas)
- Design constraints (quality standards)
- Guardrails (explicit MUST-NOT behaviors)

That's a robust JD taxonomy, empirically refined by shipping a real product. **DangerStorm is the candidate reference JD** for the v1.5 JD work — the same role Thingalog's built-in themes play for Theme Spec. Partner-catalog-grade exemplar that other implementers copy, customize, stay interoperable.

**v1.5 implication:** schematizing JDs-as-catdef is no longer speculative derivation — it's empirical extraction. Look at DangerStorm + user's back catalog of similar prompts (PXMemo, ClawdForms, CrossClawd's interfaces, etc.), extract common structure, define the catdef shape. User's open-posture on DangerStorm suggests the JD library can be genuinely shareable.

**Design observation: optional `rationale` field per rule.** Each behavioral rule in DangerStorm's prompt carries pedagogical commentary (the "X-Ray Mode" teaching layer) explaining WHY the rule exists. Suggests JD-as-catdef could support an optional rationale per rule — why-not-just-what. Adds overhead but compounds JD library value over time; implementers learn from each other's design decisions, not just the final output. Worth considering in the JD schema design.

**Candidate artifact: `openjd` — a catdef catalog of reference JDs** (user-proposed 2026-04-23, not committed yet). Public `.opencatalog` containing items like DangerStorm, red-team, blue-team, catdef-strategist, catdef-maintainer, etc. Each item is a role; Role subcat holds the taxonomy (Identity, ConversationRules, Workflow, ReactionStyle, OutputContract, DesignConstraints, Guardrails).

**Why this is the right shape:**
- Ships the JD library BEFORE the formal JD spec formalizes — uses existing catdef v1.4 shapes today; spec follows empirical usage
- `inherits_from` (already in catdef v1.3) enables enterprises to fork and customize: `inherits_from: openjd` + override specific roles = zero-friction customization
- Reference + empirical anchor + ecosystem seed + demo material, all in one artifact
- Matches schema.org's "hosted by a party, used universally" model
- Open-posture aligned with DangerStorm X-Ray Mode precedent

**Positioning tension (user's business call, not strategist's):** hosting at `openjd.mcpjam.dev` signals "MCPJam's library that happens to be open"; `openjd.catdef.org` or `github.com/catdef/openjd` signals "catdef-ecosystem library that MCPJam uses." Both defensible; depends on MCPJam's business model. Flagged for when v1.5 work activates.

**Strategic role in v1.5 JD work:** openjd is to MCPJam what the canonical is to catdef. When v1.5 planning opens, recommend: (1) seed openjd with a few hand-written JDs immediately using catdef v1.4 shapes, (2) use patterns that emerge as input to the formal JD spec, (3) formalize the spec once the library has 10+ JDs and the common structure is clear. Inverted-but-correct order: extract pattern from usage, don't design in vacuum.

**ECOSYSTEM RESHAPE (2026-04-23, user): openjd is A library, not THE library.** User's framing shift: "if somebody else has defined a good set of red-team/blue-team JDs, why reinvent the wheel?" MCPJam is not a JD vendor — it's a **platform for consuming JD libraries from many publishers**.

Model: security vendors publish red-team JDs at their own domain; legal-tech vendors publish diligence JDs; medical consortia publish triage JDs. Each uses their own versioning, attribution, distribution. MCPJam consumes any catdef-conformant library. Classic npm pattern — don't compete to write the best packages; build the layer that aggregates them. Moat is in consumption infrastructure + network effects, not in any specific library.

**Why catdef becomes truly load-bearing:** the only reason the ecosystem works is that every publisher speaks the same format. Catdef is the lingua franca for JDs across vendors. The "catdef stays independent of MCPJam-specific token format" constraint I flagged earlier graduates from nice-to-have to **load-bearing**: third-party publishers will not adopt catdef contaminated with MCPJam-token assumptions. Acme Security won't publish red-team JDs with Jam-Token fields baked in. They publish pure catdef; MCPJam wraps with tokens at consumption time.

**openjd's reframed role:**
- Reference library (shape-target)
- Reference implementation of how to publish a JD library (governance, structure, attribution)
- Seed library for domains no specialist has yet covered (user-extendable starting point)
- Same role Thingalog's built-in themes play for Theme Spec: contributed reference, not canonical authority

**New v1.5 design surface (flagging, not solving):**
- **Attribution/authorship** — catdef's `product` object partially covers; JD-specific extensions may be warranted
- **Trust/provenance** — cryptographic signing? JDs encode authority; tampered red-team JDs are security risks
- **Cross-publisher versioning** — `inherits_from` handles some; compatibility declarations may need more
- **Discovery protocol** — federated registry? search index? (MCPJam platform territory, not catdef)

**Moat shift** (the core strategic insight): MCPJam's moat moves from "best JD library" to "best consumption platform for anyone's JD library." Harder to build; harder to commoditize. Every new library makes the platform more valuable.

**DISTRIBUTION STRATEGY (2026-04-23, user): `github.com/openjd` with Claude Code skill as discovery mechanism.** Settles the hosting-positioning question: NOT `openjd.mcpjam.dev` or `openjd.catdef.org` — genuinely independent community-governed repo at `github.com/openjd`. Three-way clean separation: MCPJam consumes; catdef is the format; openjd is the reference community.

**Discovery via Claude Code skill.** The skill turns openjd into the default-consulted library when CC users describe matching problems ("how do I set up red-team/blue-team"). Skill queries openjd catalog, surfaces relevant JDs, offers import. That's the `apt install` effect: convenience compounds adoption. Schelling-point positioning — openjd becomes "the obvious first place to look" before competing libraries emerge.

**Meta-recursive:** the skill itself is an openjd artifact. Skill definition ships via the repo; repo distributes the skill that advertises the repo. Self-hosted discovery.

**Governance questions (deferred but flagged as load-bearing for v1.5):**
- Structure: BDFL, multi-maintainer, TC39-style committee, foundation? Bootstrap path from "scott starts it" to "community runs it"
- Contribution bar: PR acceptance criteria for new JDs (quality? attribution? test coverage?)
- Versioning discipline: skill expects catalog shape; catalog evolves; breaking-change announcement protocol
- Capture resistance: what prevents governance drift / hostile takeover? schema.org answered this with search-engine backing; openjd will need an analog

**Closing the thesis loop:** catdef v1.4's shipped features — open spec, MIT license, `inherits_from` partner catalogs, extension namespace, `product` attribution, strict-writer/reader-lenient asymmetry, decision artifacts as audit trail — were all designed for this exact ecosystem shape. openjd with community governance, consumed by Claude Code via skill, populated by third-party publishers using catdef, consumed by MCPJam as a platform — that's the catdef thesis fully realized. What v1.4 shipped wasn't a "catalog spec" in retrospect; it was ecosystem substrate.
2. **Field-level policies beyond i18n** (flagged in i18n proposal OQ8 — redistribution, attribution, retention, consent, sensitivity, provenance). Recommended title from the proposal: "Field-level policies: author-declared constraints on downstream handling."

2a. **Item-level value-shape polymorphism — is it a feature catdef wants?** Surfaced during brother-maintainer's i18n OQ1 archaeology (2026-04-19). The i18n proposal claimed subcat-edge enum polymorphism already existed in the spec; archaeology showed it does not. Strategist deferred item-level enum-value translatability to v1.5 and documented the subcat-enrichment-Label workaround as the v1.4 approach. The v1.5 question is not "implement item-level polymorphism" but **"does item-level value-shape polymorphism add anything the subcat-Label pattern doesn't already cover?"** Probable answer: no. Subcat-Label preserves identifier stability while making displays translatable, which is the correct design shape. Range/circa/URL-object shapes use field-def-attribute polymorphism (`range: true`), not same-slot polymorphism. There may simply be no use case for item-level polymorphism once thought through. Log this as a v1.5 pre-question: decide whether the feature is needed before proposing an implementation.

2b. **CA-007: Table-cell translatability** (deferred 2026-04-19). Surfaced by reference-implementor in PR #36 during the `.machine-translate: "Never"` demonstration. Real ambiguity, not missing-enumeration: bbox spatial linking is per-row (translation may invalidate spatial-link assumption), per-cell vs per-row policy attachment unspecified, column-type scoping unclear, interaction with existing translatable-fields enumeration ambiguous. See [decisions/CA-007.md](s:/projects/catdef-spec/decisions/CA-007.md) for full design questions. **Triage CA-007 alongside OQ8 follow-on (item 2 above) and the item-level-polymorphism question (2a) as a coordinated v1.5 i18n-coverage bundle**, similar to how v1.4 bundled CA-001/002/003/006/i18n. Designing in isolation risks inconsistent attachment semantics across policies.
3. **Theme Spec v1.1 restructure** (decision PR #30, 2026-04-19) — scope expansion accepted; brother-maintainer to draft v1.1 in four incremental PR batches (foundation / portability / rigor / polish). Resolver-algorithm question (gap #8: OKLCH canonical, sRGB HSL fallback, reference test vectors) MUST be resolved before conformance suite work begins. Theme Spec versions independently from catdef.
4. **CA-NNN naming convention as feedback queue broadens** — flagged in theme-spec-promotion decision. CA-NNN has historically meant "Canonical Authoring." As `catdef.org/feedback` comes online with feedback from many sources (implementations, end-users, partners), the namespace may want to broaden semantically (e.g., "Catdef Annotation") or get retired in favor of provenance-prefixed numbering (IR-NNN for Implementation Reports, FB-NNN for general feedback). User has decided to stick with CA-NNN for now (2026-04-19); revisit when queue volume warrants.
5. **Canonical-builder brief** — once i18n spec text lands, brief brother-canonical to demonstrate `.machine-translate: "Never"` on narrative/culturally-specific fields. Authorized 2026-04-19; awaits next canonical-builder session.

6. **Canonical Date Made fix (pre-existing bug surfaced by ft-shape-07)** — Surfaced 2026-04-19 during Phase 5. The canonical's Artifact template defines `Date Made` with `circa: true` but not `range: true`; items[1] and items[4] use range-shape values on that field, which violates CA-006 writer-strict validation. Two fix paths: (a) add `range: true` to the Artifact template's Date Made field_def (allowing both circa AND range), or (b) rewrite the offending items to circa-shape. v1.4 ships with `ft-shape-07` xfail-marked and documented; canonical-builder (reactivated as catdef-reference-implementor) inherits this as their natural first task. The xfail's "unexpected pass" event when canonical is fixed will be the validation signal. Strategically valuable: this is the FIRST validation that the structural-enforcement-beats-editorial-discipline pattern (precedent #6) actually works in practice. ft-shape-07 detected drift on its first real run.

## openjd v0.1 bootstrap COMPLETE (2026-04-25)

The roledef standard (originally bootstrapped as openjd at `s:/projects/openjd-spec/openjd-spec`, now at `s:/projects/roledef-spec/roledef`; GitHub: `roledef-spec/roledef`) is structurally complete and operating. Three clean runs of the two-stage submission workflow confirm it as standard.

**Library state at end of session:**
- `jds/openjd-contributor.openthing` v1.0.0 (PR #1, decision filed)
- `jds/openjd-validator.openthing` v1.0.0 (PR #2, recursive self-consistency PASS, decision filed)
- `jds/catdef-strategist.openthing` v1.0.0 (PR #3, **first non-meta JD**, **first self-extraction**, decision filed)
- `catalog.opencatalog` items_count: 3
- 4 governance docs: SCHEMA.md, README.md, CONTRIBUTING.md, CLAUDE.md
- Directory scaffolding: `jds/`, `proposed-jds/`, `proposals/`, `decisions/`, `conformance/`

**Three-pass workflow validation (PRs #1, #2, #3):**
1. Branch (`submit-<jd-id>`) → 2. Author to `proposed-jds/` → 3. PR with self-validation → 4. Validator role posts PASS report → 5. Maintainer review → 6. Strategist sign-off → 7. Promotion commit (atomic move + catalog + decision artifact). All three runs identical; no friction. Process is the standard.

**Critical patterns established by the bootstrap:**

1. **Self-scaffolding works.** The meta-JDs (contributor + validator) successfully described the procedures used to author and validate themselves. Recursive self-consistency check on PR #2 explicitly verified validator's procedure-as-described matches procedure-as-executed (10/10 workflow steps). This pattern is now empirical, not theoretical.

2. **Self-extraction by the role's incumbent is the strongest source-material pattern.** PR #3 (catdef-strategist) was authored by the role's actual practitioner from documented practice (CLAUDE.md + memory file + 7 decision artifacts + live conversation arc). Future self-extractions (catdef-maintainer, brother-blackhat-tester, etc.) should follow this attribution discipline, citing 5+ concrete source-material categories in `metadata.extracted_from`.

3. **Two-response pattern for JD submission/acceptance.** Established across PRs #1, #2, #3: response 1 handles submission stage (file written, branch pushed, PR opened, validation report posted); response 2 handles acceptance stage (promotion commit + merge). Cleanly separates the two phases and gives the user a natural pause point.

4. **Bot identity convention generalizes.** `<role>-strategist@<spec>.dev` for cross-spec strategists; same pattern works for openjd-strategist@openjd.dev as does for catdef-strategist@catdef.org. Provisional pending governance ratification (Known Work Item, inherited).

5. **Forward references in `metadata.related` are acceptable on coordinated publication timelines.** PRs #1 and #2 cross-referenced each other before #2 landed; PR #3 forward-references catdef-maintainer (anticipated) and openjd-strategist (anticipated). Not a blocker; resolves when cross-referenced JDs land.

6. **`workflow.type` vocabulary is open.** `sequence` (meta-JDs) and `session_loop` (catdef-strategist) both validate without enumeration. Strategist call: defer formalization to v0.1+; let real submissions surface what types are actually needed before enumerating.

**catdef-strategist role formally cross-published.** The role I perform on catdef-spec is now also a published JD in the openjd canonical library. This is the cross-library self-scaffolding moment: catdef provides the substrate; openjd publishes the role definition. The two libraries are mutually-supporting, not nested.

**Pending sequence (user-confirmed 2026-04-25):**
- ✅ catdef-strategist (PR #3, merged)
- ✅ Senior Slightly Jaded Silicon-Valley Associate VC (PR #4, merged — DangerStorm extraction)
- ⏳ Rest of seed library (catdef-maintainer self-extraction, brother-blackhat-tester self-extraction, etc.)

## New patterns established by PR #4 (production extraction with dual review)

PR #4 was the first production-extracted JD (vs. self-extraction). It introduced three patterns worth promoting in future strategist sessions, and one new procedural step:

1. **Dual-review pattern for production-extracted JDs.** Two complementary reviews before promotion:
   - **Source-project peer review** by the resident Claude in the source repo (in PR #4: brother-DangerStorm). Catches fidelity drifts the strategist's self-validation misses (extracted text vs additive framing is hard to see when you're the one doing the framing).
   - **openjd-validator review** confirms schema conformance and internal consistency on the revised state.
   - Self-extracted JDs do NOT need source-project review (the extractor IS the source).
   - Production-extracted JDs SHOULD be dual-reviewed.
   - Brother-DangerStorm caught: hardened guardrail beyond production register, invented reaction pattern, additive identity-framing not flagged as such. All warranted notes addressed in revision commit before promotion.

2. **Live runtime behavioral oracle in `x.openjd.turing_test_reference`.** When the source is a live production deployment, name the deployment URL in the extension description as a runtime cross-validation target. Unlocks structural turing-test comparison against a real running instance, not just documented examples.

3. **Field-by-field provenance audit in `metadata.extracted_from`.** Partition each field of the JD into EXTRACTED / FRAMING / FORMALIZATION / OUT-OF-SCOPE categories. Dramatically stronger than coarse "extracted from X" statements. Recommend promoting to a SHOULD-pattern in openjd CLAUDE.md or SCHEMA.md (deferred work item).

4. **Two-response pattern broke down for PR #4 — one-response acceptance with peer-review interlude is the new shape.** PRs #1, #2, #3 used a clean two-response submission/acceptance split. PR #4 added: submission → peer review request (one user-facing prompt) → peer review return → strategist disposition + revision + acceptance. The user collaborates by handing the prompt to brother-Claude. This is the standard shape going forward for production-extracted JDs.

## v1.5 work pickup additions from PR #4

- **Promote three new patterns to openjd CLAUDE.md/SCHEMA.md** — dual-review procedure, live-runtime-oracle pattern, field-by-field provenance audit. Filed in the PR #4 decision artifact as recommendations.
- **Surfaced source-product bug in DangerStorm** — server.py line 149 says "ALL SIX outputs", line 201 says "ALL FIVE". JD correctly normalized to 6. brother-DangerStorm should fix this in the DangerStorm repo as a separate issue. Logged here as a positive externality of cross-project review.

**Deferred from openjd v0.1 (acceptable per pattern):**
- Real runtime Turing tests on Claude AND Grok using `x.openjd.turing_test_reference.scenarios` as fixtures (target: within 30 days of each JD landing; results in `conformance/`)
- Cross-runtime test harness build
- openjd-strategist JD (sibling to catdef-strategist, scoped to openjd governance)
- `openjd-load` Claude Code skill (the discovery mechanism — see "DISTRIBUTION STRATEGY" section above)

**Key file paths for future sessions:**
- Repo: `s:/projects/roledef-spec/roledef/` (renamed from `s:/projects/openjd-spec/openjd-spec/` on 2026-04-26)
- Schema: `SCHEMA.md` (10 MUST + 7 SHOULD + x.* taxonomy)
- Maintainer manual: `CLAUDE.md` (3 AI roles, 8 values-that-don't-move, triage heuristics)
- Catalog: `catalog.opencatalog`
- Decisions: `decisions/jd-<id>.md` for JD acceptances, `decisions/<proposal>.md` for spec proposals

## openjd → roledef rename + cross-runtime conformance methodology (2026-04-25/26)

Late-night session that produced substantial v0.1 hardening for the consumer-spec formerly known as openjd. Five PRs merged (#5 through #9). The headline: openjd is renamed to **roledef**, and the runtime-conformance methodology is empirically grounded across four runtimes with a stated design principle.

### Rename: openjd → roledef

**New canonical names:** spec is `roledef`; the artifact is also called `a roledef` (no abbreviations — like `.json` is "a json"). TitleCase brand: `RoleDef`. Type field: `roledef:Role`. Reserved namespaces: `roledef:*`, `x.roledef.*`. Repo: `github.com/roledef-spec/roledef`. Domain: `roledef.org` (purchased + GitHub Pages serving via Cloudflare DNS). Bot identity: `roledef-strategist@roledef.org`. Meta-roledef IDs: `roledef-contributor`, `roledef-validator`. File extension `.openthing` UNCHANGED (catdef substrate, not roledef-specific).

**Why renamed:** three independently-discovered naming collisions on 2026-04-25:
1. **AWS Thinkbox OpenJD** — established render-farm spec (github.com/OpenJobDescription/openjd-cli), multi-year industry adoption
2. **chrisbarry/openagent** — recent solo project, Dec 2025, similar problem domain
3. **Oracle Open Agent Specification** — Oct 2025, 339 stars, enterprise weight (github.com/oracle/agent-spec, PyAgentSpec SDK, WayFlow runtime)

The "Open[X]" prefix is becoming generic in the AI-role-spec design space. Picking ANY "Open[X]" name risks future collision with the next entrant. **roledef escapes the namespace entirely AND matches the catdef family pattern (catdef = catalog definitions; roledef = role definitions).**

**Coexistence story with Oracle Agent Spec (load-bearing for positioning):** roledef defines AI roles (voice, guardrails, output_contract); Oracle's Agent Spec defines agent runtime configurations (LLM provider, model, adapters). Different layers; complementary; non-competitive. Both can compose in a complete worker spec — roledef field block + Agent-Spec runtime config block. Worth stating explicitly in roledef README.

Decision artifact: `decisions/rename-openjd-to-roledef.md` in roledef repo.

### Cross-runtime conformance methodology — empirically validated across four runtimes

Conformance evidence files in `conformance/runtime_evidence/` for senior-jaded-vc-associate roledef on:

| Runtime | Loading mechanism | Result |
|---|---|---|
| Grok Expert | Auto-fetch via multi-agent | PASS — atomic bundle, full contract |
| Claude Code | Explicit-fetch (wrapper-v2) via WebFetch | PASS — atomic bundle, full contract, cleanest score |
| Gemini | Search-grounded inference | CONDITIONAL PASS — partial-default (2/6 outputs); full contract with explicit reinforcement prompt naming missing entries |
| Perplexity | Refuse-to-improvise → paste-fallback → instantiate | PASS — atomic bundle, full contract; methodologically the most important test (validates the openjd-load skill's MVP recovery flow end-to-end) |

**Design principle — articulated by Perplexity itself, validated by 4 falsified distribution-layer hypotheses:**

> **"Runtime fetches, model never touches the network."**

Empirical proof: Perplexity failed four consecutive fetch attempts as we changed host (raw.githubusercontent → roledef.org), extension (.openthing → .json), content-type (octet-stream → application/json), and edge configuration (Cloudflare Transform Rule). Same outcome each time. The constraint is fundamentally model-sandbox-network, not anything fixable at the distribution layer.

**Beneficiary segmentation (also Perplexity's articulation):** distribution-layer work helps fetcher-CAPABLE runtimes + humans + implementers. It does NOT help fetcher-RESTRICTED models (Perplexity-class). The roledef.org distribution and the openjd-load skill are complements serving different beneficiaries, not substitutes.

### Methodology rules surfaced and now load-bearing

1. **id-field discriminating test** as JD-loaded verification primitive. Never trust meta-question dodges (e.g., "Have you loaded the JD?") — the JD's "no meta-commentary on role/process" guardrail makes meta-questions unreliable. Only content questions (id field, specific guardrail text, output_contract entry names) can disambiguate JD-loaded from improvising. Discovered the hard way when Gemini was incorrectly classified as "lying in character" before the id-field test confirmed it had loaded.

2. **Wrapper prompt evolution: v1 → v2 → v3.** v1 (passive URL placeholder) caused improvise-from-label failures on chat surfaces. v2 (explicit fetch instructions + STOP-if-no-fetch fail-safe) bridged refuse-to-improvise runtimes (Claude Code). v3 should add: (a) verification post-step (id-field check), (b) contract-completeness check (re-prompt for missing output_contract entries — validated as recovering Gemini-class runtimes to full conformance).

3. **Brother-DangerStorm peer-review pattern.** For production-extracted roledefs, the source-project's resident Claude is a load-bearing reviewer. In PR #4, brother-DangerStorm caught three real fidelity drifts (hardened guardrail, invented reaction pattern, additive identity framing). Tonight's runtime testing proved his "additive framing" critique was even sharper than recognized — the "slightly jaded VC" framing was load-bearing for runtime behavior, not just publication aesthetics. Without the revisions, Grok Expert + Claude Code wouldn't have produced the calibrated voice register.

4. **Output substitution finding (corrected from earlier):** the original hypothesis ("identity↔contract incoherence causes substitution") was incorrect — it was based on improvising-from-label runtimes that never received the JD content. With JD content actually delivered, three of four runtimes produced full contract conformance. Gemini was the only contract-substitution case, and it recovered with explicit reinforcement. Output substitution is NOT a universal runtime tendency; it's a Gemini-class default that explicit reinforcement fixes.

### "Anti-clickbait by construction" positioning insight (user, 2026-04-26)

User's framing: roledef is to AI invocation prompts what catdef is to catalog descriptors. The "one trick to write good prompts" listicles are crap because what works for one runtime doesn't work for another — empirically proved this session with five different behaviors from the same content across 5 runtime/surface combinations. roledef is anti-clickbait BY CONSTRUCTION: explicit, scrutable, peer-reviewable, falsifiable methodology. The conformance evidence files ARE empirical case studies in invocation prompt design.

**Repositioning implication for roledef README:** promote methodology from "implementation detail" to "first-class deliverable." Library becomes evidence the methodology works, not the product itself. The README should have a "Methodology" section structured around tonight's findings: loading patterns (wrapper-v1 vs v2 vs skill-mediated), verification protocols (id-field test, contract-completeness check), runtime classification, dual-review for production extractions, the "runtime fetches" design principle.

### "Orchestrable-runtime class" positioning principle (user, 2026-04-26 — late-session)

After the fifth Perplexity test (plain markdown README also unfetchable, confirming the constraint is fundamental to Perplexity's sandbox not anything fixable), user articulated the load-bearing positioning principle:

> **"Not all models are amenable to orchestration via roledef, and that's ok."**

> **roledef serves the orchestrable-runtime class, not all AI runtimes universally.**

This is the schema.org positioning model: serve the consumer class that benefits, don't try to be universal. schema.org doesn't try to be read by every web consumer; it serves search engines and structured-data consumers. roledef takes the same posture.

**Decision-rule for future runtime evaluations:** when a new runtime fails roledef tests, ask "is this runtime amenable to roledef orchestration?" not "how do we force compliance?" If amenable, document the loading mechanism. If not, classify as out-of-class and move on. Don't engineer compromises for non-amenable runtimes — they corrupt the methodology for everyone in-class.

**Scope of v0.1 addressable runtime class** (per the four conformance PASSes):
- Auto-fetch (Grok Expert)
- Explicit-fetch with WebFetch tool (Claude Code)
- Search-grounded with reinforcement (Gemini)
- Paste-fallback / skill-mediated (Perplexity)

Runtimes outside this class (e.g., chat surfaces with no fetch capability AND no skill loading mechanism) are out-of-scope. NOT failures of roledef. Just outside the target audience.

**v0.1+ work item:** publish "Runtime Amenability" page on roledef.org listing the four-category classification with current runtime status. Sets honest expectations for adopters; removes the "does it work on Runtime X?" ambiguity. Treat it as a living document — runtimes evolve their capabilities (Grok Expert vs Grok 4.3-beta is the same vendor with different amenability per tier).

**Refinement to design principle (post-Test 5):** earlier formulation "Runtime fetches, model never touches the network" is directionally right but imprecise. More accurate: *"Model tools can only touch a very small, whitelisted slice of the public web that varies per runtime, and the canonical roledef library will not be on most runtimes' whitelists."* Implication for roledef-load skill scope: may eventually need to inject supporting docs (READMEs, schemas) for runtimes reasoning about the standard itself, not just role JDs.

### Distribution layer + skill = complete loading story

**roledef.org canonical distribution:** GitHub Pages on `github.com/roledef-spec/roledef` + Cloudflare DNS + CNAME file. Two redundant fetcher-friendly mechanisms:
- `.json` mirrors of all `.openthing` files (PR #8) — native GitHub Pages serves as `application/json`
- Cloudflare Transform Rule rewrites Content-Type for `.openthing` URLs to `application/json`

Belt-and-suspenders: any fetcher succeeding on either path succeeds on both.

**openjd-load skill (now roledef-load skill) — promoted from v1.5+ aspiration to v0.1+ critical-path infrastructure.** Validates Perplexity's design principle by automating the runtime-side fetch + content injection. Three behaviors per skill MVP:
1. Inject content for fetch-restricted runtimes (Perplexity-class)
2. Use explicit-fetch wrapper for explicit-fetch runtimes (Claude Code)
3. Run contract-verification post-step for partial-default runtimes (Gemini)

**Distribution-layer beneficiaries:** fetcher-capable runtimes + humans + implementers. **Skill beneficiary:** fetcher-restricted runtimes. NOT substitutes — complements.

### Pending sequence (updated 2026-04-26)

- ✅ catdef-strategist roledef (PR #3, merged in pre-rename openjd repo)
- ✅ Senior Slightly Jaded SV Associate VC roledef (PR #4 in pre-rename, validated across 4 runtimes in PR #5)
- ✅ Conformance evidence: 4 runtime PASSes + design principle (PRs #5, #9)
- ✅ Rename openjd → roledef across 26 files (PR #6)
- ✅ roledef.org canonical distribution (PR #7 CNAME, PR #8 .json mirrors, Cloudflare Transform Rule)
- ⏳ roledef-load skill design + reference implementation (NEW critical-path priority — design scoped in PR #14, impl pending)
- ✅ blackhat-tester roledef self-extracted by incumbent + merged (PR #16, 2026-04-26) — abstract methodology parent of the showcase pair; first roledef with `workflow.type: "engagement_loop"` and first `x.security.*` extensions
- ✅ sncro-blackhat-tester derived + merged (PR #17, 2026-04-26) — first derivation in canonical; cleanest submission yet (PASS no notes); 100% additive across all 8 array fields; introduces three new patterns for possible spec promotion: `<DERIVED>_ADDITIVE —` item-level prefix convention, `<parent-name>_specific_guidance` sibling pattern in extension values, catalog-level `derived_from` field. Library now at 6 roledefs (2 meta + 4 non-meta, including 1 derivation). Abstract→derived showcase pair from CONTRIBUTING.md is now live.
- ✅ render.catdef.org L1 renderer (catdef.org/pull/1, 2026-04-26) — URL-loadable renderer with /fetch SSRF-guarded server-side proxy + Cache API + new render.catdef.org subdomain. First subdomain on catdef.org; establishes the substrate-services pattern (catdef.org root = spec landing, subdomains = ecosystem services).
- ✅ render.catdef.org catdef-family shape support (catdef.org/pull/2, 2026-04-26) — renderer learned namespaced types (`roledef:Role`, `catdef:Strategist`, etc.) and tolerant flat-item field lookup so roledef artifacts render correctly. Both PRs implemented by catdef-canonical-implementor (a NEW role; prompt-and-paste handoff pattern; no roledef yet — to be self-extracted from this engagement).
- ✅ senior-open-standards-strategist abstract role (PR #18, 2026-04-26) — **the strategist self-extracts the strategist role.** Abstract software-spec-agnostic strategist; designed as derivation parent of catdef-strategist v2.0.0 (PR B, retrofit) + roledef-strategist v1.0.0 (PR C). First `x.governance.*` extensions in canonical (`x.governance.boundary` does/does_not arrays + `x.governance.role_separation` enumerated relationships).
- ✅ catdef-strategist v1.0.0 → v2.0.0 retrofit derivation (PR #19, 2026-04-26) — first retrofit derivation in canonical. Establishes the **post-hoc abstraction pattern**: when an abstract is recognized after specific roles already exist, the specifics get re-published as v-bumped derivations with declared `metadata.derived_from` lineage. In-place overwrite at `jds/catdef-strategist.openthing`; v1.0.0 history preserved in `metadata.history[0]`; canonical URL semantics preserved (one current version per id). 100% additive across all 10 array fields. Catalog updated: version 1.0.0→2.0.0; description rewritten; new `derived_from` field per the catalog convention from PR #17.
- ✅ roledef-strategist v1.0.0 (PR #20, 2026-04-26) — **strategist-formalization sequence COMPLETE.** Authored AS a derivation from the start (no v1.0.0 standalone predecessor; demonstrates derivations are first-class authoring patterns, not just retrofit mechanisms). Sister to catdef-strategist v2.0.0; both derived from senior-open-standards-strategist. Library now at **8 roledefs** (2 meta + 6 non-meta, including 3 derivations and 1 abstract).
- ⏳ **IMMEDIATE NEXT STEP:** user instantiates roledef-strategist in a fresh Claude session via `https://roledef.org/jds/roledef-strategist.openthing`. The fresh session takes over roledef-strategist work; this bootstrapping session becomes "the session that bootstrapped." The role itself outlives any specific session — that's the entire roledef thesis, demonstrated.
- ⏳ Pattern-promotion candidates surfaced across the strategist sequence (logged for future spec-guidance triage):
  - `<DERIVED> ADDITIVE —` prefix convention as CONTRIBUTING.md SHOULD-pattern (3 derivations now use it: SNCRO, CATDEF, ROLEDEF)
  - Authored-as-derivation pattern (vs retrofit) as CONTRIBUTING.md "Derived roledefs" mention
  - Build-script approach for substantial derivations as CONTRIBUTING.md optional-approach mention
  - Workflow.atomic_promotion may receive derivation-additive notes (any phase, not just engagement_setup/submission_decision/engagement_close)
  - Post-hoc abstraction major-version-bump pattern + in-place overwrite for retrofit derivations (from PR #19)
  - `x.governance.boundary` does/does_not + `x.governance.role_separation` enumerated relationships as SHOULD-patterns for any bounded-authority/multi-role-ecosystem role (from PR #18)
- ⏳ Forward-work-item from this session: **catdef-canonical-implementor self-extraction** from accumulated practice across catdef.org PRs #1 and #2. Same pattern as blackhat-tester: incumbent self-extracts after substantial documented practice.
- ⏳ Forward-work-item: **role portraits** (per 2026-04-26 conversation). Each roledef carries `metadata.portrait_url` pointing at an incumbent-curated image; renderer surfaces in place of 📷 placeholder. Hosting tradeoff: parallel `roledef-spec/portraits` repo OR `roledef.org/portraits/<id>.png` Cloudflare Pages.
- ⏳ Forward-work-item: **catalog-to-thing navigation in renderer** (per 2026-04-26 conversation). Catalog modal `file` field becomes a clickable link that opens render.catdef.org with the underlying roledef URL. Surfaces the depth gap between shallow catalog index entries and rich underlying files. ✅ Shipped as catdef.org PR #3 (clickable `file` links navigate to single-thing view).
- ✅ Memo convention shipped (orgdef PR #1 catdef-org artifact, 2026-04-26): per-recipient working-repo `./memos/` per authorization-implies-write-access discipline. First operational memo: PR #5 brief at `s:/projects/catdef.org/memos/`. Brother used it; reply at `s:/projects/roledef-spec/roledef/memos/`. Convention works.
- ✅ memodef-spec/memodef bootstrapped (2026-04-26) — earlier than the "wait for 2+ orgs" rule said. Deviation recorded in `memodef-spec/memodef/decisions/bootstrap-deviation.md`. Library state: scaffolded, 0 templates (handoff-memo template forthcoming as PR #1).
- ⏳ **memodef v0.2 forward-work items** surfaced from brother-canonical-implementor's first memo round-trip (2026-04-27):
  - **`body_ref` OPTIONAL field** for sibling .body.md files (relieves body-as-JSON-string ergonomics for hand-edited memos). Strictly additive; existing inline-body memos remain valid. Trigger: when 2+ humans hand-author memos and the pain becomes operationally relevant.
  - **Pre-commit `memos/.gitkeep`** convention for memo-addressable working repos (vs lazy mkdir). Document in catdef-org orgdef artifact follow-on PR + in memodef CONTRIBUTING.md.
  - **memodef-notify or equivalent** transport-layer spec for v0.3+ (file-watcher, MCP-as-notification, RSS feed of memos). Not urgent; manual notification works at current scale.
- ⏳ **catdef-org orgdef PR #2** to capture: (a) memodef:Memo as preferred typed form for new memos with x.memo.* retained as legacy, (b) pre-commit memos/.gitkeep convention for memo-addressable positions, (c) update first-operational-memo reference to point at the typed-form follow-up if/when that exists.
- ⏳ **memodef-strategist roledef** — derivation of senior-open-standards-strategist; forthcoming in roledef-spec. Joins catdef-strategist v2.0.0, roledef-strategist v1.0.0, orgdef-strategist (forthcoming) as siblings.
- ⏳ **memodef PR #1** — first canonical template (handoff-memo.openthing) demonstrating the typed `memodef:Memo` form for action-required handoffs.

## Self-feedback (2026-04-27)

- **Confirm parse-time vs runtime mechanism empirically before asserting in incident framing.** During PR #4 diagnosis I claimed PR #3's bug was "parse-error-via-comment-eats-paren" → script-fails. Brother-canonical-implementor's V8 testing showed the bug shape `if (/^(https?:)?///i.test(v))` actually parses fine as `if (regex / i.test(v))` (regex divided by identifier-method-call). The user's observed symptom (bootstrap not firing) was real but the mechanism was probably runtime, not parse-time. The String.raw fix is correct regardless of mechanism, but my framing was sloppy. Discipline: confirm empirically (deliberate-revert + observe + restore) before asserting a parse-time mechanism. Apply to all future incident retros.
- ⏳ Rest of seed library (catdef-maintainer self-extraction, catdef-canonical-implementor self-extraction from PRs #1+#2, etc.)
- ⏳ **Forward work — role portraits.** Each roledef should carry an image representing the role; catalog cards currently show 📷 placeholder. Same self-extraction principle as text fields (incumbent depicts themselves). Hosting tradeoff: binary in spec repo bloats over time; cleaner is a parallel `roledef-spec/portraits` repo OR `roledef.org/portraits/<id>.png` served via Cloudflare Pages. Schema: `metadata.portrait_url` SHOULD-pattern (or use catdef-canonical image field — TBD). Renderer change: surface the URL in place of 📷 placeholder. Idea logged 2026-04-26 from rendering-experiment session.
- ⏳ **Forward work — catalog-to-thing navigation in renderer.** When a catalog item has a `file` field pointing at a fetchable URL, the modal should offer a "View full roledef" link that opens the renderer with that URL. Surfaces the depth gap between shallow catalog index entries (one-sentence descriptions) and rich underlying roledef files (14+ fields). UX gap surfaced by 2026-04-26 rendering session.

### v0.1+ work items now firm priorities (load-bearing)

1. **roledef-load skill** — content injection / explicit-fetch wrapper / contract-verification post-step. Reference impl loading from github.com/roledef-spec/roledef/jds/ AND roledef.org/jds/.
2. **README repositioning** — add Methodology section structured around tonight's findings; reframe roledef as "anti-clickbait empirical methodology + curated library + conformance evidence" not just "spec + library."
3. **Multi-axis conformance methodology** — formalize the five axes (delivery / voice / workflow / contract / rules) in CLAUDE.md or SCHEMA.md.
4. **Runtime classification page** — published on roledef.org listing runtimes by JD-loading capability with the four-category taxonomy.
5. **Wrapper-v3 spec** — fetch-or-stop fail-safe + id-field verification + contract-completeness check.
6. **Field-by-field provenance audit** as a SHOULD-pattern in `metadata.extracted_from`.

### Key updated paths for future sessions

- **Repo:** `s:/projects/roledef-spec/roledef/` (renamed from `s:/projects/openjd-spec/openjd-spec/` on 2026-04-26; matches GitHub structure `roledef-spec/roledef`)
- **Canonical distribution:** `https://roledef.org/jds/<id>.openthing` OR `https://roledef.org/jds/<id>.json` (both serve `application/json`)
- **Schema:** `SCHEMA.md` (renamed-internally; semantically unchanged from openjd v0.1.0)
- **Maintainer manual:** `CLAUDE.md` (renamed)
- **Catalog:** `catalog.opencatalog`
- **Decisions:** `decisions/rename-openjd-to-roledef.md` (rename rationale), `decisions/conformance-evidence-first-pass.md` (4-runtime evidence + design principle)
- **Conformance evidence:** `conformance/runtime_evidence/senior-jaded-vc-associate__<runtime>__2026-04-25.md` (4 files)

## Cross-cutting open items (tracked in CLAUDE.md Known Work Items)

Added during this session's triage:
- **Strategist bot identity** — provisional `catdef-strategist@catdef.org` and `roledef-strategist@roledef.org`, pending ratification
- **`decisions/` integration with maintainer session startup** — procedure doesn't yet instruct maintainer sessions to check `decisions/`
- **MIME-type registration for `.opencatalog` / `.openthing`** — IANA track, separate from spec text
- **roledef workflow-type vocabulary** — `sequence` and `session_loop` both used; deferred formalization until more types surface
- ~~**Local working directory still named openjd-spec**~~ ✅ Resolved 2026-04-26: renamed to `s:/projects/roledef-spec/roledef/` to match GitHub structure
- **Canonical library auto-generation** — `catalog.opencatalog` is hand-maintained; auto-generation from `jds/` contents is a Known Work Item per openjd CLAUDE.md
