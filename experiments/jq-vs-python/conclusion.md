# Result: jq vs Python JSON-pipeline reshaping

## Outcome

**Mixed; the preregistered “claim strengthened” condition was not met.**

Both implementations produced byte-identical normalized JSON on both datasets.

Source complexity:

- jq filter: **26** non-comment source lines.
- Python baseline: **36** non-comment source lines with **2** explicit loop statements.
- jq therefore used about **72.2%** as many source lines as Python.
- The preregistered threshold required jq to use **<= 60%** of Python's lines (<= 21.6 lines), so the code-size condition **failed**.

Preregistered process-level runtime medians:

- small (100 accounts / 2,000 events): jq **0.02158 s**, Python **0.97148 s**, jq/Python **0.0222x**.
- large (5,000 accounts / 100,000 events): jq **0.99000 s**, Python **1.33276 s**, jq/Python **0.7428x**.

Those runtime criteria passed the preregistered limits, but the Python numbers are heavily affected by this execution environment's site initialization. A no-op normal Python process takes roughly **1–1.6 s** here because `/opt/python-hooks/sitecustomize.py` is loaded.

## Diagnostic only — not part of the preregistered pass/fail result

Running the same Python transform with `python -S` (site initialization disabled) yielded medians of:

- small: **0.02626 s**
- large: **0.19092 s**

Against the same jq medians, that is approximately:

- small: jq **0.82x** Python
- large: jq **5.19x** Python

This diagnostic demonstrates that runtime depends strongly on the process/runtime boundary and host environment. It does **not** replace the preregistered timing, which explicitly included process startup for both implementations.

## Preregistered threshold evaluation

1. Exact normalized output equality: **PASS** on small and large.
2. jq <=60% of Python source lines: **FAIL** — 26 vs 36, or ~72.2%.
3. jq runtime <=2x Python small and <=5x Python large: **PASS** in the preregistered environment.

Because all three were required, the claim is **not upgraded**.

The weakening condition also does not hold: Python used 36 lines, exceeding the allowed <=125% of jq's 26 lines (32.5 lines), regardless of runtime.

## Interpretation

The experiment supports a narrower and more useful discriminator:

> jq is attractive when the job is *primarily a JSON expression/pipeline*, especially where avoiding explicit host-language iteration/state matters; it is not automatically dramatically shorter than concise Python for a single composite transformation, and large in-memory transforms can favor Python once interpreter-startup artifacts are removed.

Accordingly the registry should:

- keep jq confidence unchanged;
- retain the low-crossing-cost recommendation;
- add an `avoid_when` discriminator for large in-memory transformations where host-language performance or richer application logic dominates;
- attach this experiment as empirical evidence.
