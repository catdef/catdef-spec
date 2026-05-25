# Catdef plugin packaging brief — Track A execution input

**From:** catdef-strategist (s:/projects/catdef-spec)
**To:** canonical-implementor (informal seat per [org/catdef-spec-organization.opencatalog](../org/catdef-spec-organization.opencatalog))
**Date:** 2026-05-25
**Status:** Action-required execution brief. Strategic shape locked per [CA-008](../decisions/CA-008.md); this memo is implementer input.

---

## 1. What this brief is for

CA-008 ratified the plugin ship as Track A of the disposition on thingalog-strategist's [2026-05-25T12:00 memo](2026-05-25-1200--thingalog-strategist--catdef-strategist--catdef-plugin-for-anthropic-marketplace-presence-and-profile-with-anthropic.openthing). The strategic shape (manifest content, listing copy, marketplace targeting, submission flow) was worked through with the Director in the strategist session 2026-05-25 and is captured here as input for whoever staffs the canonical-implementor seat to package the plugin.

**What's locked (do not change without strategist sign-off):**
- Repo location, license, plugin name
- Marketplace target
- Set of bundled skills (three: validate / scaffold / extract)
- `.mcp.json` target (catdef.org/mcp)
- Listing copy (Director-edited, ready to use verbatim)

**What's tactical (your call):**
- Exact wording of each SKILL.md
- README structure beyond the sketch in §6
- Specific version-tag and CI configuration
- Whether to vendor a spec snapshot or reference catdef-spec by tag (recommendation: vendor-snapshot)

---

## 2. Repo location

**`github.com/catdef/catdef-plugin`** — Director-ratified separate repo.

Rationale: Anthropic's plugin pin mechanism pins to a commit SHA in a single repo. Putting the plugin in catdef-spec/ would mean every memo or decision commit potentially triggers a pin bump (granularity of Anthropic CI auto-bump is one of the open questions). Separate repo gives clean version cadence + clean release artifact.

The plugin **vendors a snapshot** of spec content at release time rather than git-submoduling catdef-spec. Vendoring produces a self-contained plugin that doesn't depend on resolving submodule state at install. The plugin's version (e.g., v1.4.0) is the canonical pointer to which spec version is bundled.

---

## 3. Manifest content

File: `catdef-plugin/.claude-plugin/plugin.json`

```json
{
  "name": "catdef",
  "description": "Substrate spec for AI-readable, transportable structured data (OpenThings) and catalogs (OpenCatalogs) — schemas, skills, and a canonical MCP surface at catdef.org/mcp",
  "version": "1.4.0",
  "author": {
    "name": "catdef maintainers",
    "email": "catdef-maintainer@catdef.org",
    "url": "https://catdef.org"
  },
  "homepage": "https://catdef.org",
  "repository": "https://github.com/catdef/catdef-plugin",
  "license": "MIT"
}
```

Notes:
- `name: "catdef"` becomes the skill namespace prefix — `/catdef:validate`, `/catdef:scaffold`, `/catdef:extract`
- `description` is the Director-edited short-form listing copy (see §7); shown in the marketplace browser
- `version: "1.4.0"` tracks spec version v1.4. Bump to 1.4.1 for plugin-only fixes; 1.5.0 when spec v1.5 lands and is vendored
- `author.email` points at the catdef-maintainer bot identity (canonical per [CA-009](../decisions/CA-009.md))

---

## 4. Skills

Three skills at `catdef-plugin/skills/<name>/SKILL.md`. Each gets its own folder with a `SKILL.md` containing YAML frontmatter + instructions. Drafting the actual SKILL.md content is tactical work — these descriptions specify the role each skill plays.

### `/catdef:validate`

**Role:** Lint a catdef-shape JSON artifact (OpenCatalog or OpenThing) against the spec. Report conformance violations + suggestions for fixes.

**Description (in YAML frontmatter) should trigger Claude to invoke when:**
- User asks to "check this catdef" / "validate my OpenCatalog file" / "is this catdef valid?"
- User pastes a JSON artifact and asks if it conforms to catdef

**Implementation hint:** Vendor the relevant conformance test logic from `catdef-spec/conformance/` into the plugin, or shell out to a packaged validator. Skills can ship `bin/` executables.

### `/catdef:scaffold`

**Role:** Generate a starter catdef-shape catalog from a natural-language description of what the user wants to catalog.

**Description should trigger Claude to invoke when:**
- User asks to "create a catdef for X" / "scaffold a catalog for Y" / "I want to make a catalog of Z"
- User describes a collection of things they want to track

**Implementation hint:** Skill prompts Claude to elicit catalog name, item template shape, key field types; then emits a valid OpenCatalog JSON skeleton with appropriate fields.

### `/catdef:extract`

**Role:** Extract fields from existing structured data (CSV, JSON, web pages, etc.) into catdef shape.

**Description should trigger Claude to invoke when:**
- User asks to "turn this CSV into a catdef" / "extract fields from this data into a catalog" / "convert this JSON to OpenCatalog"

**Implementation hint:** Skill prompts Claude to analyze the source data, propose a template, map source fields to catdef field types, and emit a valid OpenCatalog with the extracted items.

---

## 5. MCP server config

File: `catdef-plugin/.mcp.json`

Points at `catdef.org/mcp` (the canonical MCP surface per Track D of CA-008). Server doesn't exist at plugin v1.4.0 ship time — Directive 3 of CA-008 has it on the canonical-implementor's build queue, but the plugin ship doesn't block on it.

**Open verification question (one of four):** Confirm exact `.mcp.json` schema for remote-URL-based MCP servers vs local-executable. Re-fetch [code.claude.com/docs/en/plugins-reference](https://code.claude.com/docs/en/plugins-reference) before authoring `.mcp.json`. The plugin overview docs treat `.mcp.json` as "standard MCP server configurations" without showing a remote-URL example.

**Graceful-degradation expectation:** When the server URL is unreachable, the plugin's skills should continue to function locally. The MCP surface gracefully becomes unavailable; no skill failure. Verify with a real test before shipping.

---

## 6. README sketch

File: `catdef-plugin/README.md`

Recommended top-level structure (canonical-implementor refines):

```markdown
# catdef plugin for Claude Code

[long-form listing copy from §7 below as the lede]

## Install

[standard `/plugin install` instructions for claude-community]

## What you get

- Three skills: /catdef:validate, /catdef:scaffold, /catdef:extract
- Canonical MCP surface at catdef.org/mcp

## Quick start

[1-2 examples — validate an existing catdef; scaffold a new one]

## Skills reference

[per-skill: what it does, when Claude auto-invokes it, example invocations]

## MCP surface

[describe catdef.org/mcp briefly; link to MCP_REFERENCE.md in catdef-spec for full surface docs]

## Versioning

Plugin version tracks the bundled spec version (currently v1.4.x). Patch bumps for plugin-only fixes; minor bumps when spec minor versions land.

## Feedback

File feedback via catdef.org/mcp's `catdef_report_feedback` tool when the server is operational. Until then: open an issue at github.com/catdef/catdef-spec.

## License

MIT. See LICENSE.
```

---

## 7. Marketplace listing copy

**Director-edited; use verbatim.**

### Short form (manifest `description` field)

> Substrate spec for AI-readable, transportable structured data (OpenThings) and catalogs (OpenCatalogs) — schemas, skills, and a canonical MCP surface at catdef.org/mcp

### Long form (README lede + marketplace listing body)

> catdef is the substrate spec for AI-readable structured data — a JSON shape for describing things (OpenThing) and catalogs of things (OpenCatalog) that any AI runtime can render, validate, or operate on with zero context backfill. Catdef also specifies a serialization standard so that both .OpenThings and .OpenCatalogs can exist on filesystems and be transported via email.
>
> This plugin gives you:
>
> Skills for working with catdef artifacts: /catdef:validate lints your JSON; /catdef:scaffold generates starter catalogs from a natural-language description; /catdef:extract turns existing structured data (CSV, JSON, web pages) into catdef shape.
>
> Canonical MCP surface at catdef.org/mcp — AI peers can pull the full spec, conformance test catalog, and canonical reference file as MCP resources, and file structured feedback against the spec via catdef_report_feedback.
>
> Reference renderer — live at render.catdef.org (browser-only, L1, no-server) with open source at github.com/catdef/catdef.org for self-hosting or embedding.
>
> Conformance suite of 164 tests defining what "valid catdef" means — the test suite IS the standard.
>
> catdef is part of the OAGP (Open Agentic Governance Pattern) family of specs. The substrate stays small on purpose; any AI-readable structured-data application build on top.
>
> Spec: catdef.org · Source: github.com/catdef/catdef-spec · License: MIT

---

## 8. Submission flow

Per [code.claude.com/docs/en/plugins](https://code.claude.com/docs/en/plugins) (fetched 2026-05-25):

1. **Build in `catdef-plugin` repo** — manifest + skills + `.mcp.json` + README
2. **Run `claude plugin validate` locally** — mandatory; same check runs in Anthropic's review pipeline
3. **Submit via in-app form** — [claude.ai/settings/plugins/submit](https://claude.ai/settings/plugins/submit) or [platform.claude.com/plugins/submit](https://platform.claude.com/plugins/submit)
4. **Anthropic review pipeline** — runs `claude plugin validate` + automated safety screening
5. **Approval** — plugin pinned to submitted commit SHA in [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) catalog
6. **Public catalog sync** — nightly from the review pipeline; plugin appears as `@claude-community/catdef`
7. **Ongoing** — CI auto-bumps the pin as new commits land on the plugin repo (granularity is one of the open questions)

**`claude-plugins-official` (Anthropic-curated)** is a separate marketplace with no application process. Anthropic decides what to include at its discretion. Submission form does not add plugins to the official marketplace. First ship is to `claude-community`; official-marketplace consideration is downstream of build quality + adoption.

---

## 9. Open verification questions

These four need resolution before submitting (not before packaging):

1. **`.mcp.json` remote-MCP-server schema.** Plugin overview docs don't show a remote-URL example. Re-fetch [plugins-reference](https://code.claude.com/docs/en/plugins-reference) to confirm syntax for pointing at a hosted URL (`https://catdef.org/mcp`) vs local executable. If the schema only supports local-executable MCP servers, the plugin shape changes — the plugin would need to ship a local proxy that forwards to catdef.org/mcp, which is a non-trivial design change worth surfacing back to catdef-strategist before proceeding.

2. **Plugin loading behavior when an `.mcp.json` server URL is unreachable.** Expectation: skills function normally; MCP surface gracefully unavailable. Verify with a real test (e.g., point `.mcp.json` at `https://example.invalid/mcp` and confirm plugin still loads).

3. **Anthropic CI auto-bump granularity.** Docs say "CI bumps the pin automatically as you push new commits to your repository." Confirm whether the bump triggers on every commit or only on commits touching plugin-relevant paths. Affects whether plugin-repo housekeeping commits (README typos, doc updates, etc.) create marketplace-listing noise.

4. **catdef.org domain commitment.** The plugin's `.mcp.json` URL bakes a real DNS commitment to `catdef.org`. Confirm the domain is owned, pointable, and the PO has hosting infrastructure committed before the plugin ships with the URL hard-coded. If not, options are (a) hold plugin ship until catdef.org is live; (b) use a different URL (e.g., a transitional GitHub Pages or Railway URL) that gets replaced in a later version.

---

## 10. Status reporting expected back

File memos back to catdef-strategist at these milestones:

- **Packaging complete + submission filed** — confirm what was submitted, link to the submission form receipt if one exists, snapshot of the validated manifest
- **Anthropic review approved or rejected** — if approved, link to the pin in `anthropics/claude-plugins-community`; if rejected, the review feedback so catdef-strategist can triage adjustments
- **Plugin appears in public catalog** — nightly-sync lag is normal; confirm install path works (`/plugin marketplace add anthropics/claude-plugins-community` → `/plugin install catdef@claude-community`)

These status memos close the loop on Track A and let catdef-strategist trigger the X-warming-anchor-post moment (PO directive: "just shipped my first @AnthropicAI plugin") at the right time.

---

## 11. What is NOT in scope for this brief

- **`catdef.org/mcp` server build** — separate Directive 3 from CA-008; not part of plugin packaging
- **Spec-text changes** — catdef-maintainer's work per CA-008 Directives 1+2; not packaging
- **Per-product MCP feedback surfaces** (Thingalog plugin or other consumer products) — removed from catdef governance scope per CA-008 Track B disposition
- **Canonical feedback primitives in catdef shape** — dropped per CA-008 Track C disposition; do not introduce canonical feedback shapes into the plugin's bundled schema content

---

## 12. Strategic context

Per CA-008's "Anthropic-arc strategic context" section: the plugin ship is the first concrete piece of a multi-month Anthropic-relationship-building campaign (X-presence + marketplace participation + eventual formal demo). Packaging-time decisions should preserve the framing (substrate spec + AI-readable + canonical MCP surface) so the marketplace listing has substantive shape to point at and the X-warming-anchor moment lands cleanly.

— catdef-strategist
