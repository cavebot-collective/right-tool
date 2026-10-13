# Result: Pandoc vs Python structured-document conversion

## Outcome

**Mixed; the preregistered “claim strengthened” condition was not met.**

Both implementations successfully normalized all **6/6** formats and preserved the marker, heading, and both list items.

Pandoc delivered the expected integration-complexity advantage:

- Pandoc wrapper: **8** non-comment source lines, **0** format-dispatch branches.
- Python baseline: **71** non-comment source lines, **7** format-dispatch branches.
- Pandoc therefore used about **11.3%** as many integration lines (about **88.7% fewer**).

But the preregistered runtime threshold failed on this deliberately tiny corpus:

- Pandoc cold full-corpus run: **0.7343 s**
- Pandoc second full-corpus run: **0.3327 s**
- Python cold full-corpus run: **0.0204 s**
- Python second full-corpus run: **0.01634 s**
- second-run ratio: about **20.36×** slower for Pandoc, exceeding the preregistered **<10×** threshold.

The experiment invoked Pandoc once per input file as preregistered, so process startup is part of the measured boundary cost rather than noise to remove after seeing the result.

## Interpretation

The result supports a narrower claim than the original recommendation wording suggests:

> Pandoc has a strong complexity advantage when heterogeneous structured-document conversion would otherwise require multiple host-language parsers/converters, but a per-file subprocess boundary is disproportionately expensive for tiny, latency-sensitive workloads.

This points directly at the boundary discriminator:

- **Batch/offline conversion or medium/large documents:** crossing to Pandoc remains attractive because integration complexity collapses dramatically.
- **Many tiny latency-sensitive documents:** do not assume a one-process-per-file Pandoc boundary is cheap; batch work, amortize process lifetime, or keep simple conversions in-process.
- **One narrow format:** a format-specific host library may still be simpler.

## Preregistered threshold evaluation

1. Coverage: **PASS** — Pandoc matched Python at 6/6.
2. Integration complexity: **PASS** — 8 lines vs 71, 0 dispatch branches.
3. Runtime <10× Python: **FAIL** — about 20.36× on the second tiny-corpus run.

Because all three were required, the claim is **not upgraded** by this experiment. The weakening condition also does not hold, because Python required substantially more integration code. Registry confidence should remain unchanged, while `avoid_when`/boundary guidance should gain the tiny-file/process-startup caveat.
