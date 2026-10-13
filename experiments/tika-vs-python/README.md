# Tika vs Python mixed-format extraction bake-off

Status: **preregistered; results not yet run**

## Question

When a project needs normalized text extraction across a heterogeneous document corpus, does crossing the JVM boundary to Apache Tika delete enough parser-integration work to justify the crossing cost compared with a conventional Python host-language stack?

This experiment deliberately uses **Apache Tika 3.3.3** because the supported 3.x line still ships a single runnable `tika-app` JAR. Tika 4.x changes the distribution shape to a ZIP plus adjacent libraries, which would add deployment ceremony unrelated to the extraction-coverage question this first bake-off is trying to isolate.

## Hypothesis

Tika will materially improve format coverage while requiring substantially less format-specific integration code than the Python baseline.

## Corpus

Generate deterministic fixtures containing the same marker text where the format permits it:

1. plain text
2. HTML
3. XML
4. RTF
5. ZIP containing text
6. DOCX
7. XLSX
8. PPTX
9. PDF
10. EPUB

The corpus generator and fixture manifest are part of the experiment artifact.

## Compared systems

### Tika

- Apache Tika 3.3.3 `tika-app`
- Java 21 runtime
- one subprocess invocation per file
- no custom parser selection by file type

### Python baseline

A normal host-language stack using idiomatic Python libraries where needed plus stdlib format handling. The baseline may dispatch by extension/MIME because that is precisely the integration machinery being measured.

## Measurements

For each extractor:

- successful files / total files
- whether the marker text is recovered
- wall-clock time for a cold full-corpus run
- wall-clock time for a second full-corpus run
- non-comment source lines in extractor integration code
- number of format-specific dispatch branches
- runtime/install dependencies

A success means marker text is recovered from the file; merely identifying MIME type does not count.

## Preregistered decision threshold

The Tika crossing claim is empirically strengthened if all are true:

1. Tika recovers marker text from **at least 2 more formats** than the Python baseline, **or** matches coverage while requiring **<= 50%** of the baseline's format-specific integration source lines.
2. Tika requires **no per-format parser dispatch** in the experiment implementation.
3. End-to-end runtime is operationally plausible for an offline/batch extraction boundary: **< 10x** the Python baseline on this tiny corpus after JVM/tool startup is included.

The claim is weakened if Python matches coverage with comparable or less integration code and Tika adds materially higher runtime/operational burden.

## Non-goals

- This is not a benchmark of parser quality on malformed real-world documents.
- It does not evaluate OCR.
- It does not compare exact layout reconstruction.
- It does not claim Tika should replace a format-specific library when only one narrow format is required.
- It does not test Tika 4.x deployment shape; that is a separate crossing-cost question.

## Reproducibility

The final experiment directory must contain:

- corpus generator
- dependency manifest
- both extractors
- runner
- machine-readable results
- human-readable conclusion
- tool/runtime version capture

No conclusion should be merged without the raw result artifact.
