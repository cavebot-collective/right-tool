# Pandoc vs Python structured-document conversion bake-off

Status: **preregistered; results not yet run**

## Question

When a project must normalize several structured documentation/publishing formats, does invoking Pandoc delete enough format-specific host-language conversion machinery to justify the subprocess boundary?

## Hypothesis

Pandoc will match or exceed the Python baseline's format coverage while requiring substantially less format-specific integration code.

## Corpus

Generate deterministic fixtures containing the same marker phrase and simple structure:

1. Markdown
2. HTML
3. DOCX
4. EPUB
5. LaTeX
6. reStructuredText

Every fixture contains:
- one heading
- one paragraph with the marker text
- one 2-item list

## Target representation

Normalize every input to plain Markdown suitable for downstream text/document processing.

A conversion counts as successful when:
1. the marker text survives;
2. the heading survives as a heading or clearly equivalent text;
3. both list items survive.

Exact formatting fidelity is not required.

## Compared systems

### Pandoc

- installed `pandoc` executable
- one subprocess invocation per input
- one generic command path with no per-format parser implementation

### Python baseline

Idiomatic Python libraries/stdlib with explicit dispatch by input format.

The baseline may use:
- BeautifulSoup/lxml for HTML
- python-docx for DOCX
- zipfile/XML/HTML handling for EPUB
- direct/simple parsing for Markdown, reStructuredText, and LaTeX

This dispatch/integration code is part of what is being measured.

## Measurements

- successful formats / total formats
- cold full-corpus wall time
- second full-corpus wall time
- non-comment source lines in conversion integration code
- number of format-specific dispatch branches
- external/runtime dependencies

## Preregistered decision threshold

The Pandoc crossing claim is empirically strengthened if all are true:

1. Pandoc matches or exceeds Python baseline coverage.
2. Pandoc requires **<= 50%** of the Python baseline's format-specific integration source lines, or eliminates all per-format parser dispatch.
3. Pandoc total second-run time is **< 10x** the Python baseline on this tiny corpus.

The claim is weakened if Python matches coverage with comparable or less integration code and without materially greater dependency burden.

## Non-goals

- pixel-identical layout preservation
- arbitrary binary-document extraction
- OCR
- complex citation/bibliography behavior
- testing every Pandoc input/output format
- proving that Haskell is a preferable application language

## Reproducibility

Preserve:
- corpus generator
- source fixtures or deterministic encoded fixture artifact
- both converters
- runner
- machine-readable results
- human-readable conclusion
- captured tool/runtime versions

No conclusion should be written before raw results are produced.
