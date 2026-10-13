# Evidence and claim lifecycle

right-tool treats each recommendation edge as a claim that can strengthen, weaken, age, be disputed, or be retired. The registry is the durable truth; issue comments and prose reports are supporting discussion, not the canonical state.

## Evidence kinds

- **primary** — official documentation, specifications, source repositories, release notes, or other first-party material.
- **practitioner** — credible real-world reports, postmortems, community experience, or operational comparisons.
- **empirical** — right-tool project experiments, fixtures, measurements, and bake-off results.
- **research** — synthesized research reports that aggregate multiple underlying sources.

A recommendation may link several evidence records of different kinds. Broad research reports are acceptable starting evidence, but important or disputed claims should accumulate narrower primary and/or empirical support over time.

## Evidence states

Each evidence record has:

- `observed_on` — when the evidence itself was observed or captured.
- `last_checked_on` — when right-tool last verified that the evidence still supports the claim.
- `review_after_days` — freshness window.
- `status` — `current`, `stale`, `disputed`, or `superseded`.
- optional `superseded_by` — replacement evidence record.

A recommendation has its own claim state: `current`, `provisional`, `disputed`, or `retired`. Confidence is separate: a claim can be current but low-confidence, or disputed despite historically strong evidence.

## Adding or updating a claim

1. Add or update evidence records first.
2. Link the recommendation through `evidence_ids`.
3. Update the recommendation's `status`, `confidence`, `advantage`, `avoid_when`, or boundary if the evidence changes the decision threshold.
4. Run:
   ```sh
   python scripts/validate_registry.py
   python scripts/audit_evidence.py
   python scripts/sync_package_registry.py
   python scripts/generate_triage.py
   node scripts/generate_atlas.mjs
   ```
5. Commit registry changes and regenerated artifacts together.

Research findings should not live only in issue discussion. The issue can explain the investigation, but the resulting claim/evidence state belongs in the registry.

## Challenging a claim

A challenge should identify the recommendation id and the evidence or counterexample that weakens it.

- If evidence is questionable but unresolved, mark the evidence or recommendation `disputed`.
- If a replacement source supersedes an older one, mark the older evidence `superseded` and point `superseded_by` at the replacement.
- If the crossing advantage no longer clears the project's decision threshold, mark the recommendation `retired`; do not silently delete its history.
- If the claim merely needs a fresh check, leave it current until the freshness window expires, then review and update `last_checked_on`.

## Staleness

`scripts/audit_evidence.py` performs structural lifecycle checks on every PR. Staleness is reported but does not fail ordinary PRs.

A separate scheduled workflow runs the audit with `--strict-stale`. Its purpose is to make aging evidence visible without making unrelated code changes fail simply because a review date passed.

## Empirical evidence

Bake-offs should enter the registry as `empirical` evidence only after their fixtures, method, and results are preserved in the repository. The evidence record should point to that durable artifact, not merely to an issue comment summarizing the result.
