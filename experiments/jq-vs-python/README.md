# jq vs Python JSON-pipeline reshaping bake-off

Status: **preregistered; results not yet run**

## Question

When a task is fundamentally "take JSON on stdin, reshape/filter/group/join it, emit JSON on stdout," does crossing to jq materially reduce implementation complexity without imposing an unreasonable runtime penalty versus a Python stdlib script?

## Hypothesis

jq will express the pipeline substantially more compactly than Python while producing byte-equivalent normalized JSON and remaining operationally plausible for shell/pipeline workloads.

## Workload

A deterministic generator creates two datasets with the same schema:

- **small**: 100 accounts, 2,000 events
- **large**: 5,000 accounts, 100,000 events

Each document contains:

- accounts: id, name, status, region, tags
- events: account_id, category, amount, timestamp

The transformation must:

1. keep only active accounts;
2. join events to their account;
3. group by account;
4. compute event count and total amount;
5. compute sorted unique event categories;
6. preserve selected account metadata;
7. sort by descending total amount, then account id;
8. return the top 50 rows as JSON.

The jq and Python implementations must consume the same input and emit a normalized JSON array with identical semantics.

## Compared systems

### jq

- installed `jq` executable
- one filter program
- stdin → stdout
- one process per full document

### Python baseline

- Python 3 stdlib only
- one script
- stdin → stdout
- explicit dictionaries/loops/grouping as needed
- one process per full document

## Measurements

- exact normalized-output equality
- non-comment source lines in the transformation implementation
- number of explicit Python loop statements versus jq's declarative filter
- median wall-clock time across 7 runs after one discarded warm-up, for small and large datasets
- executable/runtime dependencies

Timing includes process startup for both implementations.

## Preregistered decision threshold

The jq crossing claim is empirically strengthened if **all** are true:

1. jq and Python produce exactly equivalent normalized output on both datasets.
2. jq uses **<= 60%** of Python's non-comment transformation source lines.
3. jq median runtime is **<= 2x** Python on the small dataset and **<= 5x** Python on the large dataset.

The claim is weakened if Python matches correctness, uses at most **125%** of jq's source lines, and is at least **2x faster** on both datasets.

Otherwise the result is mixed and should refine the trigger/negative discriminators without changing confidence automatically.

## Non-goals

- claiming jq is an application language
- testing streaming JSON sequences
- comparing third-party Python dataframe/query libraries
- optimizing either implementation after seeing results
- measuring network or filesystem I/O

## Reproducibility

Preserve:

- deterministic dataset generator
- jq filter
- Python baseline
- benchmark runner
- raw result JSON
- versions
- hashes
- conclusion

No conclusion should be written before raw results are produced.
