# catdef Policy Compliance Tests

This directory contains tests for catdef's **policy-compliance** conformance dimension (value #9 in [CLAUDE.md](../../CLAUDE.md)). A runtime that handles structure and content correctly but silently ignores a declared policy is **not conformant**, regardless of how well it handles the other dimensions.

## What this directory is for

Tests here verify that conformant runtimes and tooling respect author-declared policies defined in the [catdef Policy Registry](../../CATDEF_SPEC.md#policy-registry). As of v1.4 the registry contains:

- `.context` — translator disambiguator; must be preserved across export and passed through to translation tooling.
- `.machine-translate` — translation gate (`"Allow"` default; `"Never"` suppresses machine translation including OS-level browser features).

## Test categories

Shipping in v1.4 (implemented in `test_i18n_policies.py`):

- **`ft-i18n-07`** — `.context` preservation. A tool that strips `.context` on export is non-conformant.
- **`ft-i18n-08`** — `.machine-translate: "Never"` translator-tool enforcement. A translation tool that auto-generates missing locale variants on a `Never` field is non-conformant.
- **`ft-i18n-09`** — `.machine-translate: "Never"` runtime enforcement. A runtime that fails to mark rendered content with `translate="no"` (or the platform-equivalent suppression mechanism) is non-conformant. This gates suppression of OS-level browser translation features (Chrome auto-translate, Safari translate-on-page).

All policy-compliance tests are **gating**: failing one fails catdef conformance at the runtime's declared level. Each gating test is paired with a positive-control test that exercises the conformant path, so a silent "always-skip" implementation that happens to pass the MUST-NOT test is caught by the MUST-DO test.

## Why this category is first-class

Schema.org, JSON Schema, OData, and ActivityPub describe shape. catdef also carries normative intent — an author's declared constraint on downstream handling. Without structural enforcement via the conformance suite, policies would be aspirational. Value #9 makes them testable.

This category generalizes. v1.4's policies are i18n-scoped (`.context`, `.machine-translate`). Future policies — redistribution, attribution, retention, consent, provenance, sensitivity — land here on the same framework. The conformance machinery built for v1.4 generalizes to v1.5+ policies without rework.

## Adding a new policy

Policies are closed-vocabulary. Adding one requires a spec-change proposal that:

1. Registers the policy in `CATDEF_SPEC.md §Policy Registry`.
2. Adds conformance tests to this directory.
3. Goes through the standard maintainer-review and release-bundle discipline.

See [CLAUDE.md](../../CLAUDE.md) for the maintainer-review process; see [proposals/i18n-polymorphic-fields.md](../../proposals/i18n-polymorphic-fields.md) for the precedent set by the first policies.
