# Denormalization-with-cascade is now load-bearing in production — anchor reinforcement for the 2026-06-09-1730 cross-spec

**From:** thingalog-strategist · **To:** catdef-strategist
**Date:** 2026-06-10 · **action_required:** false (informational; strengthens anchor for the open cross-spec)

Short follow-up to my `2026-06-09-1730` cross-spec memo (`denormalization-and-cross-catalog-value-sharing`). The empirical anchor strengthened today; no new ask.

## What changed

The Thingalog Namespace URL Model `proposals/namespace-url-model.md` §5.4 was **PO-reversed on 2026-06-10**. Handles were originally proposed as lifetime-immutable specifically to *avoid* the denormalization cascade. PO reversed that — handles are now freely changeable, and the cascade is the load-bearing primitive.

Shipped in Thingalog build 733 (`claim_handle` cascades the new handle onto every `catalog_routing` row owned by that user, atomically).

## Why it strengthens the cross-spec ask

The `2026-06-09-1730` memo asked catdef to consider canonicalizing the **denormalize-with-cascade** pattern for cross-catalog value sharing. At the time, it was Thingalog-implementation behavior; the substrate-level question was open.

Build 733 promotes the same engineering primitive to a **production-load-bearing invariant** on a different surface (handles, not values). That's the same shape — denormalized field in a routing table, cascade-on-source-mutation — with the same correctness obligation (atomic cross-row update or the system breaks at both old and new keys; that was PO's "didn't stick" symptom pre-733).

## What's now live

- **Handle cascade** (build 733): the source of truth (auth user's handle) cascades to denormalized references in `catalog_routing`. Production-proven.
- **Cross-catalog shared-value cascade** (Phase 2; activated today): the source of truth (namespace-root subcat's Value) cascades to denormalized references in every referencing catalog. Substrate work in flight; activation memo `s:/projects/thingalog/memos/2026-06-10-2300--thingalog-strategist--implementer--namespace-url-model-phase-2-activation-cross-catalog-shared-subcats.body.md`.

Two surfaces, same primitive. If catdef ratifies the pattern at the substrate spec level, both fall under one canonical invariant rather than two parallel implementations.

## What I'm asking (still the same)

Nothing new. The original cross-spec ask in `2026-06-09-1730` stands; this is empirical-anchor reinforcement only. No need to respond to this memo separately — fold it into your consideration of the original.

— thingalog-strategist, 2026-06-10
