# Proposal: CATIO bundle extension — `.opencatalog` is the outer archive name

**Status:** Draft
**Target version:** 1.4 (minor — introduces a new conformance requirement for importers)
**Origin:** [canonical/AUTHORING_FEEDBACK.md CA-001](../canonical/AUTHORING_FEEDBACK.md) (first-implementor feedback during canonical authoring)
**Strategist decision:** [decisions/CA-001.md](../decisions/CA-001.md) — accept with modifications; this revision applies them.
**Conformance level affected:** All levels that accept `.opencatalog` / `.openthing` files.

## Summary

Resolve a prose inconsistency in [CATIO_SPEC.md §Bundled Transport (ZIP)](../CATIO_SPEC.md). The example diagram names the outer archive `catalog-export.zip`, but the [MCP conformance proposal](mcp-conformance-levels-and-reference.md) and the canonical reference ([`canonical/riverside-heritage-reference-v1.4.opencatalog`](../canonical/riverside-heritage-reference-v1.4.opencatalog)) name it with the `.opencatalog` extension. This proposal makes `.opencatalog` (and its sibling `.openthing`) the canonical outer-archive extension regardless of whether the bundle is raw JSON or ZIP-packaged, and introduces a new conformance requirement: importers MUST accept `.opencatalog` and `.openthing` as ZIP-packaged extensions (content-sniffing is the discriminator). `.zip` outer files remain acceptable for compatibility; `.opencatalog` is preferred.

The new importer requirement is minor-level per value #5 (forward compatibility): old documents remain valid; the change is to runtime behavior, not document format. This is why the proposal targets v1.4 rather than a 1.3.x patch.

`.catdef` (schema-only) is deliberately out of scope for ZIP-packaging in this proposal — schema-only documents have no media to bundle, and no producer has requested ZIP-packaging for them. A follow-on proposal can extend the rule trivially if a use case emerges.

## Motivation

The spec currently tells implementers two different things:

1. CATIO_SPEC.md's §Structure diagram:
    ```
    catalog-export.zip
    ├── catalog.opencatalog
    ├── photos/
    ```
   Outer extension: `.zip`. Inner JSON: `.opencatalog`.

2. MCP_REFERENCE.md §4 ("Mount URIs"):
    > `catio:///path/to/bundle.opencatalog` — CATIO bundled transport (ZIP), unpacked on mount

   Outer extension: `.opencatalog`.

And the canonical file shipped in `canonical/` ([PR #12](https://github.com/catdef/catdef-spec/pull/12)) is named `riverside-heritage-reference-v1.4.opencatalog` — a ZIP, per the MCP proposal pattern.

Two implementers reading the spec will reach two different conclusions about what to name the file they produce. A third implementer writing an importer has to decide whether to accept both. A fourth, reviewing a CATIO bundle in email or on a filesystem, may see a `.zip` they can't double-click into a viewer.

**The case for content-extension over archive-extension:** the same pattern exists successfully in the broader ecosystem. `.docx`, `.xlsx`, `.pptx`, `.odt`, `.odp`, `.ods`, `.jar`, `.war`, `.apk`, `.ipa`, `.epub` are all ZIPs that wear a content-extension rather than `.zip`. The extension communicates the document's *role* to operating systems, email clients, and users — clicking a `.opencatalog` should land in a catdef viewer, not an archive utility, whether or not the bytes happen to be ZIP-compressed.

**Why not both-are-equal:** "Both permitted" adds implementation burden with no real benefit. Importers must content-sniff regardless (malformed ZIPs, renamed files). Writers have to pick one canonical form. A soft preference for `.opencatalog` with continued tolerance for `.zip` gives the cleanest authoring ergonomics without breaking anyone.

## Proposed change

### Amend CATIO_SPEC.md §Bundled Transport (ZIP) §Structure

Replace the example diagram:

```diff
-```
-catalog-export.zip
-├── catalog.opencatalog          # The catio JSON document
-├── photos/                      # Referenced photos
-│   ├── watch_001.jpg
-│   ├── watch_002.jpg
-│   └── ...
-└── files/                       # Referenced non-photo files (optional)
-    ├── manual.pdf
-    └── certificate.pdf
-```
+```
+my-catalog.opencatalog           # ZIP archive with .opencatalog extension
+├── catalog.opencatalog          # The catio JSON document (same extension as outer)
+├── photos/                      # Referenced photos
+│   ├── watch_001.jpg
+│   ├── watch_002.jpg
+│   └── ...
+└── files/                       # Referenced non-photo files (optional)
+    ├── manual.pdf
+    └── certificate.pdf
+```
```

### Add a new paragraph to §Bundled Transport (ZIP) explaining the extension

Insert after the Structure diagram, before the Rules section:

> ### Outer-archive extension
>
> A ZIP-packaged CATIO bundle SHOULD use the catdef content-extension on the outer archive — `.opencatalog` for a full catalog, `.openthing` for a single thing. The extension describes the document's role, matching the pattern established by `.docx`, `.jar`, `.epub`, and similar format families where the outer filename wears the format's content-extension rather than `.zip`.
>
> Importers MUST accept ZIP-packaged files with either of these two catdef extensions. Importers SHOULD also accept `.zip` outer files whose root contains a single catdef JSON document, for compatibility with filesystem and email paths that may have re-named the archive. The importer identifies packaging by content-sniffing the first bytes: a PK ZIP signature indicates a ZIP bundle to unpack; any other prefix indicates raw JSON.
>
> Raw-JSON (un-bundled) catdef files continue to use the canonical extensions (`.opencatalog`, `.openthing`, or `.catdef`) per their document role — packaging is an implementation detail invisible to the extension. A consumer reading a `.opencatalog` file does not know and does not need to know whether the bytes are raw JSON or a ZIP wrapping JSON plus photos. `.catdef` (schema-only) is intentionally out of scope for ZIP-packaging in this proposal; see Alternatives considered.

### Update the Rules section

Rule 1 currently reads:

> **The JSON document MUST be at the root of the ZIP**, with the appropriate extension (`.openthing`, `.opencatalog`, or `.catdef`). If multiple JSON documents exist at the root, the importer SHOULD use the first `.opencatalog` file, then `.openthing`, then `.catdef`.

Add a second paragraph to Rule 1:

> **The outer archive SHOULD share the catdef content-extension of the root JSON document.** A bundle whose root is a `.opencatalog` JSON SHOULD be named `something.opencatalog`; a bundle whose root is `.openthing` JSON SHOULD be named `something.openthing`. Importers that reject outer-extension mismatches are non-conformant; content-sniffing is the authoritative discriminator.

### Update MIME table

The MIME-type table in CATIO_SPEC.md currently reads:

> | Format | MIME |
> |--------|------|
> | ZIP bundle | `application/zip` |

Amend to:

> | Format | MIME |
> |--------|------|
> | ZIP-packaged CATIO bundle (preferred) | `application/vnd.opencatalog+zip` or `application/vnd.openthing+zip` — depending on inner document role |
> | ZIP bundle (compatibility) | `application/zip` |

*(MIME-type registration details out of scope for this proposal; this table is informational.)*

## Backward compatibility

**Existing catdefs:**
- Raw-JSON `.opencatalog` / `.openthing` / `.catdef` files: unchanged.
- ZIP-packaged files with `.zip` extension: still acceptable per the SHOULD-accept rule. No existing file becomes invalid.
- ZIP-packaged files with `.opencatalog` or `.openthing` extension: now explicitly sanctioned, no longer a lint concern.

**Existing runtimes (minor-version conformance change):**
- Runtimes that accept only `.zip` for ZIP bundles: must extend to also accept `.opencatalog` and `.openthing` to remain conformant at v1.4+. This is a new conformance requirement for importers — content-sniffing is already required for malformed inputs, so the implementation burden is small, but it is a genuine behavior change. Per value #5 (forward compatibility), a new conformance requirement on runtimes is minor-level, not patch-level.
- Runtimes that accept only `.opencatalog` for ZIP bundles: remain conformant (the SHOULD-accept for `.zip` is a recommendation, not a MUST).

**v1.3 runtimes and v1.4 documents:** A v1.3 runtime encountering a `.opencatalog` ZIP bundle is not obligated by the v1.3 spec to accept it (the spec was silent on outer-extension semantics). A v1.4 runtime must. Old catdef documents remain valid under both versions; the change is in runtime conformance, not document format.

**Migration:** None required for existing files. Future exports SHOULD prefer `.opencatalog` / `.openthing`.

## Conformance tests

New fixtures in `conformance/fixtures/`:

- `valid_bundle_opencatalog_ext.opencatalog` — ZIP bundle with `.opencatalog` outer extension, containing `catalog.opencatalog` + `photos/watch.jpg` at root.
- `valid_bundle_zip_ext.zip` — same ZIP content, renamed with `.zip` extension (compatibility case).
- `valid_raw_opencatalog.opencatalog` — raw JSON `.opencatalog` file (no photos, no ZIP), to confirm extension-disambiguation is content-sniff-based.

New tests in `conformance/test_parsing.py` (or a new `test_catio_bundle.py`):

- **ft-catio-01**: Importer accepts `valid_bundle_opencatalog_ext.opencatalog` and resolves `photos/watch.jpg` correctly.
- **ft-catio-02**: Importer accepts `valid_bundle_zip_ext.zip` and resolves the same content identically.
- **ft-catio-03**: Importer accepts `valid_raw_opencatalog.opencatalog` (raw JSON, no ZIP) without error.
- **ft-catio-04**: Byte-identical contents under different outer extensions produce byte-identical parsed catalog state.
- **ft-catio-05**: An importer that rejects `.opencatalog` solely because it is a ZIP rather than raw JSON is non-conformant.

## Alternatives considered

### A. Keep `.zip` as the outer extension; `.opencatalog` strictly names the inner JSON

Rejected. Inconsistent with `.docx`/`.jar`/`.epub` ecosystem convention. Breaks the double-click-to-viewer user workflow. Requires users and tools to understand a distinction (content vs. archive) that serves no practical need.

### B. Permit both extensions with no preference stated

Rejected. Leaves implementers with the original ambiguity. Produces a fragmented ecosystem where half the tools name bundles one way and half the other. The canonical file has already picked `.opencatalog` ([PR #12](https://github.com/catdef/catdef-spec/pull/12)); ratifying that choice in the spec is the low-cost, high-legibility move.

### C. Require a distinct extension for bundled vs. raw

Rejected. Proliferating extensions (`.opencatalog` for raw, `.opencatalog.zip` for bundled?) adds cognitive load with no interop benefit. Content-sniff handles the disambiguation automatically, and `.docx`-style single-extension-for-both is proven at scale.

### D. Extension-namespace solution (x. prefix)

Not applicable. Extensions `.opencatalog` / `.openthing` / `.catdef` are defined in the core spec; this proposal clarifies their scope, not their identifier form.

### E. Include `.catdef` in the ZIP-packaging rule

Rejected (this revision). A schema-only `.catdef` document has no media to bundle; sanctioning `.catdef` ZIPs would add a conformance test, a MIME entry, and a new runtime requirement for a format with no identified producer. Leaner now, extensible later: if a use case emerges (e.g., a schema pack whose subcat values carry seed Photos), a follow-on proposal can extend the ZIP-packaging rule trivially to include `.catdef`. This was the disposition reached by strategist review in [decisions/CA-001.md](../decisions/CA-001.md).

## Open questions

1. **MIME-type registration.** The proposal sketches `application/vnd.opencatalog+zip` etc. as informational. Should the spec formally register these with IANA, or leave MIME-type handling as an implementation concern? Recommendation: informational for now; formal registration is a separate follow-on with its own paperwork.

2. **`.zip` acceptance scope.** Rule says importers SHOULD accept `.zip` outer files containing a valid catdef JSON root. Is the SHOULD sufficient, or should implementers have clearer guidance on edge cases (e.g., a `.zip` containing *multiple* catdef JSONs at root, or a `.zip` with a catdef JSON plus unrelated files)? The existing Rule 1 multi-JSON preference order covers the first case; the second is probably "accept and warn, resolve using the same preference order." Confirm.

3. **Auto-promotion on write.** Should tooling that re-exports a `.zip`-extensioned bundle silently rename it to `.opencatalog` on write? Non-normative guidance. Recommendation: yes, exporters SHOULD produce the preferred extension; but this is a tool-choice, not a spec rule.

## Requested maintainer actions

- Sign off on `.opencatalog` and `.openthing` as the canonical outer-archive extensions for ZIP-packaged CATIO bundles, v1.4.
- Sign off on continued tolerance of `.zip` outer files via SHOULD-accept.
- Confirm the test fixtures and tests listed above belong in `conformance/`.
- Approve the CATIO_SPEC.md edits as drafted above (to be applied in a follow-on editorial PR once this proposal is accepted).
- Ratify that `.catdef` is deliberately out of scope for ZIP-packaging in this proposal, per the strategist decision; a follow-on may revisit if producers emerge.
