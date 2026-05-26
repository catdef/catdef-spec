# catdef reference renderer (L1)

This directory holds the canonical browser-only L1 reference renderer for catdef artifacts (`.opencatalog`, `.openthing`, `.catdef`).

A single self-contained `index.html` file — HTML structure, CSS in `<style>`, JavaScript in `<script>`. No build step, no dependencies, no server required. Drop a catdef file on the page (or pass `?url=<file>` if your host provides a fetch proxy) and a working browse/search/detail UI comes out the other side.

## Relationship to the hosted instance

The hosted instance at [render.catdef.org](https://render.catdef.org) serves this file via Cloudflare Workers. The Worker also provides a server-side `/fetch?url=` proxy that the page uses for the `?url=` bootstrap (SSRF-guarded; not included here — it requires a runtime). The Worker source lives in the private `catdef.org` operations repo (per [decisions/CA-015.md](../decisions/CA-015.md) and [decisions/CA-016.md](../decisions/CA-016.md): hosting + deploy + secret-handling stay private; spec content + reference artifacts stay public).

When the canonical renderer changes here, the hosted instance picks it up automatically — `catdef.org`'s Worker fetches `index.html` from `raw.githubusercontent.com/catdef/catdef-spec/main/renderer/index.html` at request time with edge caching (5-minute TTL).

## Conformance scope

This renderer is the **L1 reference implementation**. Per [CATDEF_SPEC.md](../CATDEF_SPEC.md) and the conformance levels in [MCP_REFERENCE.md §8](../MCP_REFERENCE.md), L1 means:

- Browser-only, no server required
- Reads catdef JSON from a local file (or remote URL via host-provided proxy)
- Renders the catalog/thing with no context backfill

A renderer that passes the L1 portions of the conformance suite at [conformance/](../conformance/) is a conforming L1 implementation. This renderer is the reference: when a question arises about "what does L1 require?", the answer is "what this file does, plus what the conformance suite checks."

## Self-host

Three paths:

### 1. Single-file local viewer

Download `index.html` and open it in any modern browser:

```sh
curl -o catdef-renderer.html https://raw.githubusercontent.com/catdef/catdef-spec/main/renderer/index.html
open catdef-renderer.html  # macOS; Linux: xdg-open, Windows: start
```

Drop a `.opencatalog` / `.openthing` / `.catdef` file on the picker. No `?url=` bootstrap (no fetch proxy in this mode).

### 2. Static hosting (no fetch proxy)

Serve the file from any static host (GitHub Pages, Netlify, S3, nginx, etc.). All features except the `?url=` bootstrap work. Users can still drop files into the picker.

### 3. Hosted with `?url=` bootstrap

If you want users to be able to load remote catalogs via `?url=https://...`, provide an SSRF-guarded `/fetch?url=` endpoint that returns the JSON. The hosted catdef.org instance does this via a Cloudflare Workers proxy with:

- `https://` only
- Hostname / IP blocklists for private space (RFC1918, link-local, loopback, CGNAT, etc.)
- Redirect handling with re-checks against the SSRF guard
- Content-Length cap + streamed-read cap (default 5 MB)
- Wall-clock timeout (default 10 s)

Implement an equivalent if you want full feature parity. The renderer expects `/fetch?url=<encoded>` to return the upstream JSON body verbatim with status 200 on success, JSON `{ error }` on failure, and an `X-Upstream-Url` header carrying the final URL after redirects (used for relative-path resolution inside catalog entries).

## Embed

The renderer is a single HTML page; embedding is mostly a question of how you frame it. Two common shapes:

### iframe with `?url=` bootstrap

```html
<iframe
  src="https://render.catdef.org/?url=https://example.com/my.opencatalog"
  width="100%" height="600"
  style="border: 0;">
</iframe>
```

The hosted instance handles the cross-origin fetch via its proxy; your page doesn't need CORS configuration on the source.

### Self-hosted with theme variables

The renderer reads theme variables from the loaded catalog's `product.theme` and applies them to CSS custom properties (`--accent`, `--bg`, `--panel`, `--ink`, `--muted`, `--border`). Authors can match the renderer to their catalog's brand without editing the renderer source.

## What this directory does NOT contain

Per [CA-016 Build Directive 1](../decisions/CA-016.md):

- **No MCP server source** — that lives in the private `catdef.org` repo and is documented in [MCP_REFERENCE.md §15](../MCP_REFERENCE.md)
- **No deploy configuration** — Cloudflare Workers config, GitHub Actions workflows, `wrangler.toml`, etc. stay private
- **No secret-handling helpers** — api-key issuance, MCP-config registration scripts are operational tooling
- **No SSRF `/fetch` proxy implementation** — that's a hosting-layer concern; if you self-host with `?url=` bootstrap, you implement your own

These all belong to the hosting layer, not the spec layer. Their absence here is the point: this directory is the *public* canonical renderer source.

## Changes and contributions

The renderer source evolves through the standard catdef proposal-and-decision pipeline. Changes affecting L1 conformance behavior need a proposal artifact ([proposals/](../proposals/)) and conformance-test coverage ([conformance/](../conformance/)). See [CONTRIBUTING.md](../CONTRIBUTING.md).

Cosmetic/UX changes that don't touch L1 conformance can land via PR directly; the catdef-maintainer reviews against:

- Single-file constraint (no external dependencies; no build step)
- Browser compatibility (modern evergreen; no IE; no ES2020+ features that lock out older Firefox/Safari)
- Embedded JS syntax discipline — the file was previously a `String.raw`-tagged template literal in TypeScript; backslash-eating bugs in regex literals were a recurring failure mode. Standalone as a `.html` file there's no template-literal escape processing, but if anyone re-embeds it into a tagged template, the discipline still applies.
- Accessibility — keyboard navigation, screen reader hints, color contrast

## Tooling

A small JS-syntax smoke test used to live in `catdef.org/tests/embedded-js-syntax.js` for the template-literal era. Now that the renderer is a standalone `.html` file, the smoke test is unnecessary; any HTML/JS validator picks up syntax issues directly. The catdef-maintainer may add a renderer-level conformance test under `conformance/` if needed.

## License

Same as catdef-spec: MIT. See [LICENSE](../LICENSE).
