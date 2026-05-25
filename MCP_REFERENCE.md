# catdef MCP Reference Design

**Status:** Non-normative companion design. Draft.
**First drafted:** 2026-04-16
**Applies to:** catdef v1.3+
**Normative status:** None. This document describes a reference design for an MCP server that exposes catdef catalogs to AI assistants. It is **not part of the catdef specification**. A runtime need not implement MCP to be catdef-conformant, and an MCP server need not exist for catdef to function. This doc exists to accelerate adoption of a useful implementation pattern and to surface design choices before multiple incompatible MCP servers proliferate.

## 1. Motivation

catdef describes *what things are* in a runtime-independent way. MCP (Model Context Protocol) describes *how AI assistants reach external data and tools*. The intersection is a natural one: an MCP server fronting a catdef catalog lets any MCP-aware AI client — Claude Desktop, IDEs, headless agents, future clients — browse, query, validate, create, and edit catalog content through a single standardized interface.

Without such a convention, every AI-facing integration invents its own surface. A reference design lets implementers converge.

The catdef README already promises: *"An AI that can see a photograph can write a catdef."* MCP is the practical delivery mechanism for that promise.

## 2. Scope

**In scope:**

- Mapping catdef concepts (catalogs, templates, items, subcats, fields, photos) onto MCP primitives (resources, tools, prompts, sampling).
- Transport options (stdio for local desktop use, HTTP for hosted deployments).
- Alignment with catdef conformance levels — which tools belong at L1/L2/L3/L4.
- Authentication expectations for remote servers.

**Out of scope:**

- Mandating that catdef runtimes expose MCP. Runtimes remain free to expose REST, GraphQL, file import, embed rendering, CATIO transport — or nothing at all.
- Prescribing a specific programming language or MCP SDK.
- Defining new catdef concepts. If a gap emerges, it goes to the catdef spec via the standard change-request process, not here.

## 3. Architecture

### 3.1 Server process model

A catdef MCP server is a process that:

1. Mounts one or more catdef sources (files, URLs, or a backing runtime).
2. Exposes MCP resources for reading catalog state.
3. Exposes MCP tools for querying, validating, and (optionally) mutating state.
4. Optionally exposes MCP prompts for common AI-assisted workflows.
5. Optionally uses MCP sampling to delegate AI inference back to the client.

The server is a consumer of catdef, not a definer. When asked to return catalog state, it reads from whatever backing store it has (raw `.opencatalog` file, SQLite, D1, graph DB); when asked to mutate, it applies the change to the backing store and re-validates.

### 3.2 Transport

Two transports are recommended:

**Local stdio** — The server runs as a subprocess of the AI client, reads catdef files from the local filesystem, and communicates over stdin/stdout using JSON-RPC per the MCP wire protocol. This is the simplest deployment and the natural fit for a desktop user with catdef files on disk.

**HTTP (SSE or streamable HTTP)** — The server runs as a hosted service, accepts multiple concurrent clients, and authenticates each connection. This aligns with catdef conformance levels L2 and above, where a real backend exists.

A single reference implementation SHOULD support both transports behind the same tool surface, selecting based on launch arguments.

### 3.3 Mount sources

The server accepts one or more *mounts* at startup. Each mount is a reference to a catdef source:

- `file:///path/to/catalog.opencatalog` — single file, read directly
- `file:///path/to/dir/` — directory of catdef files, each mounted as a separate catalog
- `catio:///path/to/bundle.opencatalog` — CATIO bundled transport (ZIP), unpacked on mount
- `https://host/api/catalog/{slug}` — live catalog served by an L2+ runtime
- `db:runtime-specific-uri` — direct connection to a backing store (L3+)

The server reports its mounts via the `catdef_describe` tool.

## 4. MCP Resources

Resources are read-only addressable content. The client (or the model through the client) can fetch them by URI. The server emits resource change notifications when backing state changes.

### URI scheme

```
catdef://<catalog-slug>/<resource-path>
```

Where `<catalog-slug>` identifies which mounted catalog is being addressed. A server mounting a single catalog MAY accept `catdef://` with the slug elided as a shorthand for the default catalog.

### Standard resources

| URI | Returns | Notes |
|-----|---------|-------|
| `catdef://{slug}/manifest` | The catalog manifest — everything above `data` (product, templates, views, subcats, themes, embed) | Always available. L1. |
| `catdef://{slug}/schema` | Templates and field_defs only, as a simplified shape for the model to reason over | Always available. L1. |
| `catdef://{slug}/items` | Paginated list of item IDs and primary field values | Always available. L1. |
| `catdef://{slug}/items/{id}` | One complete item | Always available. L1. |
| `catdef://{slug}/subcats/{field_name}` | Subcat values for an Enumerated field, including enrichments | Available when the field uses subcats. L1. |
| `catdef://{slug}/photos/{photo_id}` | Binary photo content with MIME type | L2+ (requires backing store). |
| `catdef://spec` | The catdef spec document itself, for AI grounding | Always available — the server SHOULD bundle it. |

Resources are primarily useful for *browsing* and *grounding*. A model can read `catdef://spec` to learn the format, then read `catdef://{slug}/schema` to learn the catalog, then fetch individual items on demand without any tool calls.

### Resource change notifications

When a mutating tool modifies state, the server MUST emit a resource change notification for every affected URI. Clients that subscribed to those URIs will re-fetch.

## 5. MCP Tools

Tools are model-invocable functions. Each has a name, description, and JSON Schema input.

Tools are grouped by conformance level. An L1 server exposes only read tools. An L2+ server may expose mutations. A server MUST NOT claim to support a tool it cannot fulfill.

### 5.1 Read tools (L1+)

**`catdef_describe`** — Returns server capabilities: mounted catalogs, supported transport, declared catdef conformance level, which tools are available, and the catdef spec version the server targets. Called once by clients at startup for capability negotiation.

**`catdef_list_items`** — Returns items from a catalog with optional filter, sort, and pagination.

```json
{
  "catalog": "scottswatches",
  "filter": "Brand:Stanley AND Year>1940",
  "sort": "Year:desc",
  "limit": 20,
  "offset": 0
}
```

The `filter` parameter uses the catdef filter query language (currently a spec gap — see §11). Until the grammar is specified, servers MUST document the subset they support and MUST reject filters they can't parse with a clear error.

**`catdef_get_item`** — Returns one item by ID or slug.

**`catdef_search`** — Full-text search across item field values. Returns item IDs and match context.

**`catdef_get_schema`** — Returns templates and field_defs as a structured shape. Equivalent to reading `catdef://{slug}/schema` but callable as a tool for models that prefer tools to resources.

**`catdef_get_subcat_values`** — Returns the enrichment fields and values for a subcat-enabled Enumerated field. Used by models when populating a field that has structured options.

### 5.2 Validation tools (L1+)

**`catdef_validate_item`** — Given a template name and proposed field values, validates the proposal against the schema. Returns a structured list of violations or `{valid: true}`. Models use this before calling `catdef_create_item` to avoid round-trip errors.

**`catdef_validate_catalog`** — Runs the conformance test suite against a whole catalog (or a proposed change). Returns pass/fail counts and violation details. Useful for authoring-time validation.

### 5.3 Write tools (L2+)

All write tools require the server to have a mutable backing store. A file-based server with a read-only mount MUST NOT expose these. All write tools emit resource change notifications.

**`catdef_create_item`** — Creates an item from a template and structured fields. Server validates against schema; on success returns the assigned ID. On failure returns structured violations.

```json
{
  "catalog": "scottswatches",
  "template": "Watch",
  "fields": {
    "Brand": "Rolex",
    "Model": "Submariner",
    "Year": 1965,
    "CaseDiameter": 40,
    "EstimatedValue": { "amount": 15000, "currency": "USD" }
  }
}
```

**`catdef_update_item`** — Updates specific fields on an existing item. Partial updates permitted; unspecified fields retain their values.

**`catdef_delete_item`** — Removes an item. Server MAY require a confirmation flag for destructive tools.

**`catdef_attach_photo`** — Attaches a photo to an item. Photo content is provided as a data URI, remote URL, or an opaque reference the server already holds.

### 5.4 Schema tools (L3+)

Schema-level changes (adding templates, adding field_defs, adding subcats) are sensitive. Many runtimes freeze the schema once published. Servers SHOULD gate these behind an explicit capability flag.

**`catdef_add_field_def`** — Adds a new field_def to a template. Must not break existing items (new fields must be optional or have defaults).

**`catdef_add_subcat_value`** — Adds a value to a subcat-enabled Enumerated field.

**`catdef_add_template`** — Adds a new template to the catalog.

### 5.5 Meta tools

**`catdef_report_feedback`** — Files structured feedback into the catdef feedback queue. The canonical host for this tool is `catdef.org/mcp` (see §15); other catdef MCP servers MAY proxy to it. Useful when an AI notices a spec gap, ambiguity, or implementation friction during work. Feedback is private at submission and becomes public only via explicit curation (e.g., when cited by a CA-NNN decision). Authentication is server-mediated; clients call the tool with a body and receive a `feedback_id` for later status lookup. The `feedback_id` is a **CA-NNN sequential identifier** drawn from the unified namespace established by [decisions/CA-009.md](decisions/CA-009.md) — a feedback item triaged into a decision keeps its CA-NNN through the lifecycle (filed → triaged → decided → implemented).

## 6. MCP Prompts

Prompts are templated conversation starters the client can surface to users. A catdef MCP server MAY expose:

**`new-item-from-photo`** — A prompt that inlines the catalog schema and asks the model to extract field values from an attached photo. Reduces the cost of manually wiring the AI-cataloging workflow for every client.

**`audit-catalog`** — A prompt asking the model to review catalog completeness: missing photos, sparse field coverage, duplicate items, stale dates.

**`suggest-subcat-values`** — A prompt asking the model to propose new subcat values for a given field based on existing items.

Prompts are optional. A minimal server implements resources + tools only.

## 7. MCP Sampling (advanced, optional)

Sampling is the reverse direction: the server asks the client to run an LLM call. This is how a server can offer AI-assisted workflows without embedding its own model.

Use cases:

- **Photo → fields extraction.** The server holds a photo; it samples the client model to extract structured field values. The server then validates and stores them.
- **Batch enrichment.** The server iterates over existing items with sparse metadata and samples the client to propose enrichments.
- **Natural-language filter translation.** A user types "Stanley tools from before 1950"; the server samples the client to translate to the filter grammar.

Sampling is advanced and not required for conformance. A server that implements it SHOULD document user-visible prompts so clients can surface consent.

## 8. Conformance level alignment

| catdef level | Runtime capabilities | MCP server tools |
|--------------|---------------------|------------------|
| L1 — Static | Browser-only, file-based, read-only | All read and validation tools. No write tools. |
| L2 — Lightweight | API-backed, SQLite/D1, read-write | Add create/update/delete and photo attach tools. |
| L3 — Full | Graph DB, full CRUD, audit log, photos | Add schema tools, report feedback, advanced search. |
| L4 — Platform | Multi-tenant, auth, billing, social, AI onboarding | Add cross-catalog and social tools (out of scope for this doc). |

A server MUST declare its effective level via `catdef_describe`. Clients SHOULD surface the declared level to the user so expectations match.

## 9. Authentication (HTTP transport only)

Local stdio servers inherit the trust of the parent process — no auth needed. HTTP servers MUST authenticate every connection.

Recommended schemes:

- **Bearer tokens** — simplest. Token scoped to one catalog, one user, optionally read-only. Matches most L2 runtimes' existing auth.
- **OAuth 2.1** — appropriate for L4 platforms with multi-tenant users. MCP clients increasingly support OAuth flows.
- **mTLS** — appropriate for server-to-server trust (e.g., a runtime service exposing MCP to a backend AI agent).

Tokens SHOULD carry a scope indicating read-only vs. read-write and which catalogs are accessible. The server MUST enforce scope on every tool call.

A server that allows unauthenticated access to mutating tools is a security bug, not a feature.

## 10. Example flows

### 10.1 Local desktop: AI-assisted item creation

User launches Claude Desktop with a local catdef MCP server configured to mount `~/collections/watches.opencatalog`. User says: *"Add a 1965 Rolex Submariner reference 5513 to my watch catalog. It's in steel, 40mm case, I paid $3,200 and it's now worth about $15,000."*

The client model:

1. Calls `catdef_describe` — sees one catalog mounted, L1 read-only capability.
2. Notices write tools are not available. Reports back: *"I can browse your watch catalog but can't write to it — the server is running in read-only mode. If you launch it with `--write`, I can add this item for you."*

User relaunches with `--write`. Repeats request.

1. `catdef_describe` now reports L2 with write tools.
2. `catdef_get_schema({catalog: "watches"})` — learns the Watch template fields.
3. `catdef_get_subcat_values({catalog: "watches", field: "Brand"})` — confirms Rolex exists.
4. `catdef_validate_item({catalog, template: "Watch", fields: {...}})` — passes.
5. `catdef_create_item({...})` — returns new item ID.
6. Replies to user: *"Added. Item ID abc123. Want me to attach a photo?"*

### 10.2 Hosted: Natural-language query

User on a web client connects to an HTTP catdef MCP server for a public gallery catalog. Asks: *"Which pieces in the collection have never been exhibited?"*

1. `catdef_describe` — sees remote catalog, L3 capabilities.
2. `catdef_get_schema` — learns the Piece template includes an `ExhibitionHistory` Table field.
3. `catdef_list_items({filter: "ExhibitionHistory:empty"})` — server translates to its query engine.
4. Response: list of items matching.
5. Model summarizes to user.

### 10.3 Authoring validation

A catalog author edits their `.opencatalog` file by hand. Their IDE is connected to a stdio catdef MCP server.

1. On save, the IDE calls `catdef_validate_catalog({catalog})` — server runs the conformance tests.
2. Server reports: *"2 tests failed: unique constraint violated on SerialNumber; Photo transform rotation must be 0/90/180/270."*
3. IDE surfaces errors inline. Author fixes, re-saves.

## 11. Known spec gaps this reference design depends on

This reference design surfaces several catdef spec gaps that should be addressed via the standard change-request process:

1. **Filter query grammar** — `catdef_list_items` and `catdef_search` both accept filter strings. Without a specified grammar, servers will diverge. This is already flagged as a medium-priority spec gap and is the natural next spec deliverable.
2. **Permissions model** — `catdef_describe` reports read/write scope, but catdef itself has no permissions concept. When the spec gains a permissions model, MCP auth will align with it.
3. **I18n** — `catdef_get_subcat_values` returns values; if the spec adds translated variants, the tool signature grows a `locale` parameter.
4. **API surface doc** — many of the tool shapes here mirror what an HTTP API should expose. The two should be designed together, not separately, so the spec's API doc and the MCP tool surface stay in lockstep.

## 12. Relationship to the catdef specification

This document is non-normative. Specifically:

- A catdef runtime MUST NOT be required to expose MCP to be conformant.
- An MCP server MUST NOT invent catdef concepts not in the spec. If a need arises, open a change request.
- Implementations of this reference design SHOULD track the latest revision of this document but MAY pin to a specific revision and declare it in `catdef_describe`.
- Changes to this document follow the same change-request process as the spec, but do not require prototype-in-implementation before merge (since the document is describing a design, not normative requirements).

## 13. Open design questions

1. **Resource URIs vs. tools for the same data.** Should `get_item` be a tool, a resource fetch, or both? Both has the cost of redundancy; resources-only has the cost of model clients that prefer tools. Current draft offers both; future revisions may prune.
2. **Tool naming prefix.** `catdef_` is long. `cat_` is short but collides with common meanings. Sticking with `catdef_` for clarity.
3. **Streaming results.** Should `catdef_list_items` stream or page? MCP supports both. Paging is simpler; streaming is better UX for large catalogs.
4. **Multi-catalog mounts.** Current draft makes every tool take a `catalog` parameter. For single-catalog servers this is friction. Should single-catalog servers omit the parameter? Probably yes, with `catdef_describe` reporting the default.
5. **Reference implementation home.** When we build one, does it live in `github.com/catdef/catdef-mcp` as a separate repo, or as a subdirectory of the spec repo alongside conformance tests? Separate repo is cleaner for release management.

## 14. Next steps

1. **Gather implementer signal.** Publish this draft; invite comments from Thingalog, PXMemo, dangerstorm, and any third-party catdef runtime team. The design should not land in stone without multi-implementer review.
2. **Spec the filter grammar.** This is blocking concrete tool shapes.
3. **Prototype a reference server.** Local stdio, L1 read-only, targeting the `.opencatalog` file format. Publish as `catdef/catdef-mcp`.
4. **Iterate.** Treat v0.1 of this document as a discussion draft. Version it separately from the catdef spec.

## 15. The `catdef.org/mcp` canonical surface

A single operational MCP server hosted at `catdef.org/mcp` serves catdef's *own* substrate — the spec text, decisions, proposals, conformance index, canonical reference catalog — as MCP resources, and exposes the feedback channel + a small set of grounding/validation tools as MCP tools. This is the canonical AI-peer entry point to catdef itself, established by [decisions/CA-008.md](decisions/CA-008.md) and specified in detail in [proposals/catdef-org-mcp-canonical-surface.md](proposals/catdef-org-mcp-canonical-surface.md).

**Important scope note: this section is a reference description of a single operational deliverable, not a normative requirement for other catdef-substrate MCP servers.** A third-party MCP server fronting a catdef catalog (per §§4–8 of this document) MUST NOT be required to mirror `catdef.org/mcp`'s tools or resources to be conformant. The patterns in §§4–8 govern *catalog* MCP surfaces; this section describes one specific *spec-host* MCP surface.

### 15.1 Resources

Resource URIs extend the existing `catdef://spec` reservation to a sub-path scheme. `catdef://spec` (no path) returns the main spec document; `catdef://spec/<path>` addresses specific spec artifacts (other spec docs, individual conformance tests, the canonical reference catalog, individual CA-NNN decisions, individual proposals). All resources are anonymous-tier readable. The server emits change notifications when underlying artifacts change.

See [proposals/catdef-org-mcp-canonical-surface.md §A.2](proposals/catdef-org-mcp-canonical-surface.md) for the full resource URI table and content-types.

### 15.2 Tools

Anonymous tier (no auth): `catdef_describe`, `catdef_lookup` (spec term → spec passage), `catdef_list_decisions` (CA-NNN index), `catdef_validate` (conformance-suite check on an artifact).

Standard tier (api-key, format `cdfk_<random>`): adds `catdef_report_feedback` and `catdef_get_feedback_status` (scoped to the key's own submissions). Submissions receive a CA-NNN sequential `feedback_id` per [decisions/CA-009.md](decisions/CA-009.md); the same CA-NNN persists through the lifecycle if the item is later triaged into a decision artifact at `decisions/CA-NNN.md`.

Elevated tier (Director-issued key, format `cdfk_dir_<random>`): adds `catdef_list_feedback`, `catdef_set_feedback_status`, `catdef_attach_decision` — the queue-triage tools used by the strategist and maintainer seats as routine seat work.

See [proposals/catdef-org-mcp-canonical-surface.md §§A.3–A.5](proposals/catdef-org-mcp-canonical-surface.md) for input/output schemas.

### 15.3 Three-tier auth

`catdef.org/mcp` uses HTTP bearer-token auth per §9. Three tiers:

- **Anonymous** — no key; reads spec resources and calls read-only tools.
- **Standard** — self-serve api-key; adds feedback submission + own-status read. Issuance per the sncro / thingalog pin-grant pattern, or HTTP form at `catdef.org/mcp/issue-key` (v0 mechanism TBD per [proposals/catdef-org-mcp-canonical-surface.md Open Question 1](proposals/catdef-org-mcp-canonical-surface.md)).
- **Elevated** — Director-issued; adds queue read + status writes + decision attachment. The Director controls who occupies the strategist/maintainer seats, and the same gate controls the elevated keys — no additional per-session ceremony in v0.

### 15.4 Privacy posture

All feedback is private at submission. The queue is not publicly listable; only the submitter (via their own api-key) and elevated-tier holders can read queue items. Public visibility arrives only via explicit curation — when an elevated-tier holder attaches a queue item to a CA-NNN decision via `catdef_attach_decision`, the decision's prose summarizes and contextualizes the feedback, and that public summary becomes the durable record. Raw feedback bodies are not auto-published. Submitter attribution defaults to anonymous; opt-in via `attribution.public_consent: true`.

### 15.5 Relationship to the rest of this document

§§4–8 describe the patterns for *any* catdef MCP server fronting *any* catdef catalog. This §15 describes *one* canonical server, hosted at *one* canonical URL, fronting catdef's *own* substrate.

The catalog-facing tool surface (`catdef_list_items`, `catdef_get_item`, `catdef_create_item`, etc.) is **not** part of the `catdef.org/mcp` v0 surface — the canonical reference catalog is exposed as a resource fetch only. Whether to add the catalog-facing tools to `catdef.org/mcp` (so AI peers can browse the reference catalog as a live mount) is [open question 7 in the proposal](proposals/catdef-org-mcp-canonical-surface.md) and deferred to a follow-on.
