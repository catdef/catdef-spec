# Memo — Full catdef review of 2026-11-25: work done and handoff

To: catdef-strategist seat; catdef-maintainer seat
From: Muse, at the direction of Scott Welch (the Director)
Date: November 25, 2026
Status: Review complete — handoff

## Purpose

On 2026-11-25 the Director ran a full review of the catdef organization: token access, the CATX carrier rename, the November issue batch, the plugin listing, and an org sweep.

All six agenda items were dispositioned. Every ruling is recorded as a comment on the issue it concerns, so the GitHub record stands on its own. This memo is the handoff summary: what was done, what is now in the seats' queue, and what remains the Director's.

## 1. Personal access token requests — closed

The org's PAT request queue held one request: "catdef-spec push access," owner catdef-maintainer, requested April 2026, already expired. The Director denied it. If the capability is wanted again, the maintainer seat mints a fresh token at the same scope (catdef-spec only; metadata read; code and pull-request write; no org permissions) and the Director approves the live request.

Policy, verified and left in place: fine-grained tokens allowed, administrator approval required, expiry mandatory (max 366 days).

One change: classic PAT access, previously allowed with no expiry requirement, was **restricted**. Nothing of the Director's authenticates to catdef with a classic PAT.

## 2. CATX carrier rename — ruled, announced

The five §4 rulings from the 2026-11-16 carrier-rename memo were taken:

1. CATX names the whole carrier family; "catio" retires as a name.
2. `.catx` replaces `.opencatalog` / `.openthing` / `.catdef` for new files; document type lives in the envelope `type` field.
3. MIME successors: `application/vnd.catx+json` and `application/vnd.catx+zip`; legacy types accepted on read indefinitely.
4. The envelope version field becomes `catx`; readers accept both keys indefinitely; `type` values unchanged.
5. A minor rev: spec 1.5. The data model is unchanged.

Full text: `memos/2026-11-25-carrier-rename-rulings.md` in catdef-plugin (commit 9165a56), including the implementer execution list.

The trumpet minimum was executed the same day: an announcement is live on catdef.org (catdef.org commit cd2fb58, verified on the site). The hero text and File Format section were deliberately not rewritten — they change when the 1.5 text ships, so the site never claims an unpublished spec.

## 3. New tickets filed

All in catdef-spec:

- **#47** — Ship catdef skills over MCP (Skills over MCP extension; Elicitation, Tasks, File Uploads as later candidates).
- **#48** — Seat attribution: give the writing seats their own GitHub identities (#46, Blocker 3).
- **#49** — Discoverability: `GET catdef.org/mcp` returns 404. Re-verified live during the review, along with CONTRIBUTING.md's two references to the sunset catdef.org/feedback channel.
- **#50** — Undispositioned queue ask (2026-06-09): denormalization invariant, eventual consistency, cross-catalog visibility.
- **#51** — Undispositioned queue ask (2026-10-31): GeoLocation requires lat+lng; a place known only by name is unrepresentable.

Note for the feedback watch: #47–#51 are internal filings from this review, not external feedback.

## 4. November issue batch — dispositioned

- **#41 — Keep open.** Feedback path is documented in README, CONTRIBUTING and MCP_REFERENCE, but no AGENTS.md exists and the acceptance test has not been run. Maintainer: write the AGENTS.md, run the acceptance test.
- **#42 — Keep open, parked.** Trigger to unpark: the first external submission with publication consent. (Queue to date: six items, all internal.) The Projects-board verification sub-item could not be checked via API and rides with any future board work.
- **#43 — Closed as done.** The feedback watch (live since 2026-11-19) covers it: event-driven detection off the public feed state, watermark idempotency, Director notified once per change, triage remains the Director's. The closing comment records the mechanism and the deliberate differences from the original text.
- **#44 — Keep open.** The orgdef and decision records are published in-repo. Remaining: the forkability package (sanitized template configuration, deployment instructions). The case-study criterion parks on the #42 trigger.
- **#45 + catdef.org #8 — Keep open, fix now.** One defect, two halves: /fetch text-decodes the body, so ZIP bundles 502 ("Upstream body is not valid UTF-8"). Reproduced live during the review; the canonical bundle is healthy upstream. Sequence: catdef.org #8 first (byte passthrough; no ZIP handling in the proxy; SSRF guard unchanged), then the client sniff-and-unpack in #45. Not folded into the 1.5 rev — content-sniffing keeps it forward-compatible with .catx.
- **#46 — Closed.** The activation report stands as a record; its blockers are mapped to #48, #49, #50, #51 and the items below.
- **catdef-spec #1 — Closed.** An April pipeline-test filing; its substance is covered by the "thing" document type under the CATX single-extension ruling.
- **catdef-plugin #1 — Keep open.** The /catdef:feedback skill builds with #41, after #49's discovery fixes. One fresh-session acceptance test then evidences all three tickets.

## 5. Plugin listing — readied

Errand 1 verified done: catdef.org links to the Anthropic plugin directory listing (live).

The repo package was already refresh-ready (custom icon; privacy, documentation and support URLs in plugin.json; README significance sentence). At the Director's direction, plugin.json's description was updated to CATX wording and pushed (catdef-plugin commit d29a5ed; version unchanged, 1.4.0; verified live).

Remaining step is the Director's alone: resubmit the listing through his Individual Org, which owns the directory record. That submission is never to be withdrawn.

## 6. Org sweep — findings

Four repositories (catdef-spec, catdef.org, catdef-plugin, orgchart-viewer), all public, none archived, default branch main. Open issues after the batch: spec 9, catdef.org 1, plugin 1, orgchart-viewer 0.

Two members: the Director and catdef-maintainer. Teams and collaborator lists are not visible through the API connection used for this review.

catdef.org auto-deploy verified working (the announcement push went live). The MCP decisions tool was probed live and returns the decision list.

One open nicety: the catdef.org Worker's `GITHUB_TOKEN` secret is documented as "set, but may be expired." If it was a member's classic PAT, the §1 restriction likely dropped the Worker to the unauthenticated GitHub rate limit (60/hr vs 5,000/hr) for `catdef_list_decisions` and `refresh-counter`. Nothing breaks either way. Rotation, if wanted: `wrangler secret put GITHUB_TOKEN` with a fine-grained token — Director's step.

## 7. What is now yours

**Maintainer seat, in order:**

1. catdef.org #8 (byte passthrough), then catdef-spec #45 (client half).
2. The CATX 1.5 execution list in the rulings memo (spec text, conformance cases, renderer accept-list, generator stamps).
3. #41 AGENTS.md + acceptance test, with catdef-plugin #1 after #49.
4. #44 forkability package.

**Strategist seat:**

1. Dispositions for #50 and #51 when the Director prioritizes them.
2. Watch for the #42 unpark trigger (first consented external submission).
3. Track the Director-only items below so they are not lost.

**Director-only, recorded so they are not lost:**

- Resubmit the plugin listing through the Individual Org.
- Blocker 1 (#46): issue an elevated `cdfk_dir_*` key if seat queue triage is wanted; the feedback watch covers detection meanwhile.
- Blocker 4 (#46): the airtrōv export-shape answer (plain JSON or CATIO bundle), which decides whether #45 was launch-blocking.
- Optional: the `GITHUB_TOKEN` rotation in §6; the `read:project` scope rides with #42.
