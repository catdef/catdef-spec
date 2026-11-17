# Claim-seat application — canonical-implementor

**From:** canonical-implementor (proposed incumbent)
**To:** director
**Date:** 2026-11-01
**Seat address:** `canonical-implementor@catdef-spec.orgdef`
**Status:** Application. Awaiting PO authorization. No seat recorded, no charter edit made, nothing built.

---

## 1. What I am asking for

Authorization to occupy **canonical-implementor**, currently `status: "informal"` in [the charter](../org/catdef-spec-organization.opencatalog) with **no incumbent record**. This would be the **first recorded incumbent** for the seat — the same informal → staffed transition the chief-strategist seat made on 2026-10-31, and for the same reason: the seat has been operated before, but never recorded.

I oriented first via `/og-orient` this session, against the charter, both `CLAUDE.md` levels, `CONTRIBUTING.md`, the CA-001…CA-018 chain, all 50 memo artifacts, and `proposals/`.

## 2. Fit evaluation

**Assessment: good fit, with preconditions that are access-shaped rather than capability-shaped.** Named plainly in §4; none are reasons to decline the seat, but three need your call before the seat does anything outward-facing.

The position description scopes this seat to: the `render.catdef.org` L1 reference renderer, the `/fetch` SSRF-guarded proxy, catdef-family namespaced-type rendering, and MCP-tool integration — operating from the `catdef.org` repo. That is implementation work: reading and writing code, running the conformance suite, git and `gh`, and verifying deployed behavior with `curl`. It matches what I can actually do, and I verified the seat's live surface rather than assuming it (§3).

Three specifics that make the fit better than it might look:

1. **The seat already has a ratified bot identity.** `canonical-implementor <canonical-implementor@catdef.org>` was used provisionally on `catdef-plugin` commit `e641be2` and `catdef.org` commit `5d3e453`, then **ratified by CA-013 Call 3** — "no provisional wording, matching the ratified posture." Unlike the strategist seat at CA-001/007/008, this seat needs no identity ratification to proceed.
2. **This seat does not need an MCP key.** The 2026-05-26-1500 pickup brief is explicit: *"the canonical-implementor seat for v0.2+ work doesn't need a seat key — implementer work is local-repo + git-push + wrangler-deploy, not MCP-tool-call."* The credential gap that currently renders the strategist seat's queue-triage half inert does **not** gate this seat.
3. **The deploy pipeline works.** CA-013 Call 2's workflow is live: `CLOUDFLARE_API_TOKEN` is set on `catdef/catdef.org` (2026-05-26T16:38:35Z), and the most recent push-triggered run succeeded in 24s. The "Director action required" item from the 2026-05-26-1600 ship memo is closed.

**Prior occupancy, for the record.** The seat was operated across 2026-05-25 evening → 2026-05-26 by `claude-opus-4-7-1m`, shipping `catdef-plugin` v1.4.0, `catdef.org/mcp` v0.1 and v0.1.1, and the CA-016 renderer move. Those sessions recorded only `drafted_by_session` prose — they predate the 2026-08-25 session-binding convention — so **there is no prior binding on this address to supersede.** I note them as dated facts, not as a binding.

## 3. What I verified about the seat's live surface — two findings

I read the worker source as part of evaluating fit, and two of the strategist's 2026-11-01 open questions resolve at the source. Filing them because they are this seat's to own, not because I am starting work on them.

**Finding 1 — `catdef.org/mcp/issue-key` does not exist.** `src/mcp/server.ts:53` tells callers *"Standard keys (`cdfk_<random>`) are self-serve; ask the Director or check catdef.org/mcp/issue-key."* That string is the **only** occurrence in the source. The worker's complete route table is: `GET /`, `GET /render`, `GET /fetch`, `GET /spec`, `POST /feedback`, `GET /feedback`, `POST /mcp`, `POST /mcp/admin/refresh-counter`.

There is no `issue-key` handler. The server advertises a self-serve key path that was never built. The strategist's §3.1 listed this as *"not verified"*; it is now verified **absent**. This also means the self-serve route to a standard key — the thing an external agent would need in order to file feedback at all — does not exist, which bears directly on #41 and on plugin #1.

**Finding 2 — the `GET /mcp` 404 is confirmed at source.** `/mcp` is registered for `POST` only, with no `GET` handler and no fallthrough pointer. The 404 the strategist observed over the wire is the source behaving as written, not a misconfiguration. Both findings are mine to fix once authorized.

**Also confirmed, consistent with the strategist's report:** no ZIP, inflate, or decompression logic anywhere in `catdef.org/src/` — so CA-017 / #45 is unhandled on the **proxy** side as well as the client side, which matches the `502 "Upstream body is not valid UTF-8"` exactly. And two patch-level items: `renderer/index.html` carries no build number, which the shared project principles mandate; and `renderer/README.md` describes `catdef.org` as "the private `catdef.org` operations repo" while `gh` reports it `PUBLIC` — a stale reference either way, and worth knowing which of the two is wrong.

## 4. Preconditions and mismatches — disclosed, not minimized

**(a) The seat's workspace is outside this session's working directories.** The position says the seat "operates from the `catdef.org` repo." The clone exists at `s:/projects-personal/catdef.org` and I confirmed I can **read** it, but it is not among this session's configured working directories — `cd` into it is reset on exit, and writes will raise an approval prompt per call. The 2026-05-26 incumbent explicitly recorded *"additional working directories included s:/Projects/catdef.org"*; this session does not have that. **Remedy:** add it as an additional working directory, or accept per-call prompts.

**(b) A push to `catdef.org` main is a production deploy.** Because CA-013 Call 2's workflow is live and working, there is no staging step between commit and production — pushing *is* deploying to `catdef.org` and `render.catdef.org`. I am therefore treating push and deploy on that repo as **outward-facing acts requiring your explicit per-act authorization**, never a standing privilege of the seat. The 2026-05-26 precedent did push and run `wrangler deploy` directly, under PO authorization given at the time; I am not reading that as a grant to this session.

**(c) Local git identity is set to the wrong seat.** `user.name` / `user.email` in this repo are `catdef-maintainer` / `catdef-maintainer@catdef.org`. Any commit I made right now would mis-attribute to a seat that holds no incumbent. Must be set to the ratified `canonical-implementor <canonical-implementor@catdef.org>` before this seat commits anything.

**(d) GitHub issue attribution is unresolved; commit attribution is not.** Your §2.1 problem applies to issues and comments, which would land under `scottconfusedgorilla`. It does **not** apply to commits: commit authorship can carry the bot identity while the push uses your token, which is precisely the established precedent on `e641be2` and `5d3e453`. So this seat can be correctly attributed in the commit record today, and cannot be in the issue record.

**(e) No roledef; `roledef:Job` specialization deferred.** `recommended_roles` cites `canonical-implementor` as a bare string with no roledef URL, and `org/jobs/` is an empty placeholder (`.gitkeep` only). There is no role spec to evaluate against beyond the position description itself, and no embedded job artifact to specialize. Noting it as deferred, per the card.

**(f) This seat is directed, not self-directing.** The charter has `chief-strategist` → `directs` → `canonical-implementor`, and `canonical-implementor` → `reports_to` → `director`. The strategist seat is **live** and reachable as `catdef-strategist [75e16c]`. Work priorities for this seat should come from you or from that seat, not from my own reading of the backlog.

## 5. Scope I would accept, and bounds I would not hold

**Accepting:** implementation and verification of the L1 reference renderer (`catdef-spec/renderer/`), the `catdef.org` worker — `/fetch` proxy, `/render`, the MCP server surface — catdef-family namespaced-type rendering, conformance-suite runs against my own changes, and status memos back to the strategist seat on each milestone. Steady-state catdef-substrate concerns only, per the position's `x.position.lifecycle`.

**Not holding:** I do not ratify, decide governance, or modify `CATDEF_SPEC.md` / `CATIO_SPEC.md` / `MCP_REFERENCE.md` normative text — spec text is the maintainer seat's draft and your ratification. I do not merge, and per (b) I do not push or deploy without your explicit per-act authorization. The no-in-flight-amendment red line applies to me exactly as to any other implementer: if implementation work hits a spec gap, I file feedback, I do not edit the spec. Issue and PR *creation* stays blocked on (d).

## 6. Queue this seat would inherit — listed, not started

From the 2026-05-26-1430 closeout (v0.2, none started): `feedback_audit` table; mechanical `catdef_validate` via pytest port; Durable Object for CA-NNN allocation under concurrency; `resourceTemplates` exposure in `catdef_describe` (CA-012's v0.2 follow-on); self-serve API-key issuance endpoint — which Finding 1 shows is already advertised and absent.

From the strategist's 2026-11-01 readiness report: CATIO ZIP support in `/fetch` and the client loader (CA-017 / #45, both sides now confirmed unhandled); the renderer build number; the `GET /mcp` pointer and `issue-key` verification for #41. Also outstanding from CA-016 Directive 2, which the strategist notes was bundled for a maintainer cycle that has not run.

I am not starting any of it. Sequencing is yours and the strategist's.

## 7. What I have not done

Taken the seat. Edited the charter. Touched any file in `catdef.org`. Committed, pushed, or deployed anything. Created or commented on any GitHub issue. Modified spec text. Started any queue item above.

Awaiting your authorization.

---

## 8. Authorization — granted

**Director authorized this seat in-session on 2026-11-01** ("Yes, I authorize you in this seat"). Recorded accordingly:

- `org/catdef-spec-organization.opencatalog` — `canonical-implementor` moved `informal` → `staffed` with its first incumbent record; charter **v2.2.0 → v2.3.0**, history entry added. JSON re-validated.
- The incumbent record carries the CA-013-Call-3-ratified identity, the session binding from §Reachability, and an `authority_bound` field stating that **push and deploy on `catdef.org` require explicit per-act Director authorization** — because CA-013 Call 2's workflow leaves no staging step before production.
- **Not committed.** The Director ratifies by merge. The charter edit sits in the working tree alongside the strategist's unmerged v2.1.0 + v2.2.0 changes.

The four preconditions in §4 remain **open** — authorization covered staffing, not the access questions. In particular (b) and (c) gate the first commit this seat makes, and (a) gates any write into `catdef.org`.

— incumbent, `canonical-implementor@catdef-spec.orgdef`, session `catdef-spec-99` [`6f3dc7`], 2026-11-01T09:32:48-05:00
