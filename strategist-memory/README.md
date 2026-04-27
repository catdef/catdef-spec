# strategist-memory/

The catdef-family strategist's working-state memory file. This is the bootstrap-era unified memory file that has served all four strategist roles (catdef-strategist, roledef-strategist, orgdef-strategist, memodef-strategist) during the multi-spec bootstrap.

## What's in this file

`project_catdef_strategist_role.md` carries:

- **Pending sequence** — what's next on the strategist's docket (in-flight PRs, forthcoming submissions, anticipated work)
- **Pattern observations** — emerging patterns surfaced by recent submissions, candidates for promotion to spec text
- **Forward-work items** — deferred work waiting for triggers (e.g., "bootstrap memodef when 2+ orgs adopt x.memo.* with consistent shape")
- **Cross-cutting concerns** — items that span multiple specs in the catdef family
- **Self-feedback** — strategist disciplines learned from incidents (e.g., "confirm parse-time vs runtime mechanism empirically before asserting")
- **Key paths and conventions** — quick-reference for future strategist sessions

## Why this lives in catdef-spec

catdef-spec is the foundational catdef-family member. The strategist memory file currently spans all four catdef-family consumer specs (catdef + roledef + orgdef + memodef); placing it in catdef-spec acknowledges that catdef is the substrate on which the others depend.

This is a **bootstrap-era expedient**, not the long-term shape. Forward-work item: split per-strategist memory files, one per strategist role, each living in its own strategist's working repo:

- `catdef-strategist`'s memory → `catdef-spec/strategist-memory/`
- `roledef-strategist`'s memory → `roledef-spec/roledef/strategist-memory/`
- `orgdef-strategist`'s memory → `orgdef-spec/orgdef/strategist-memory/`
- `memodef-strategist`'s memory → `memodef-spec/memodef/strategist-memory/`

Cross-cutting items would either get duplicated or live in a shared location (TBD when the split happens).

## Sync convention

The strategist memory file is the working-state institutional memory of an AI session arc. It SHOULD be kept current with every meaningful state-change:

- Every PR merged or shipped
- Every emergent pattern observed
- Every forward-work item identified
- Every self-feedback discipline logged
- Every cross-spec coordination item

The local source-of-truth for the file is the per-machine Claude state at `<HOME>/.claude/projects/<project-root>/memory/project_catdef_strategist_role.md`. **Both directions need to sync** — this committed copy is updated from the local file, and the local file is restored from this committed copy when starting a fresh session on a different machine.

A simple two-way sync would commit the memory file at session-end (when a notable state-change happened) and restore from this committed copy at session-start. Today (2026-04-26) this is manual; future tooling could automate.

## Bootstrap-era audit trail (for future reference)

This file was first committed 2026-04-26 in response to the human-steward's preparation for a desktop→laptop transition. Until then, the strategist memory file was local-only and didn't sync across machines via git. Committing it solves the cross-machine portability gap.
