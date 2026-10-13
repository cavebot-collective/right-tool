# Result: Tika vs Python mixed-format extraction

## Outcome

**Mixed; the preregistered “claim strengthened” condition was not met.**

Both systems recovered the marker text from **10/10** formats:

- plain text
- HTML
- XML
- RTF
- ZIP containing text
- DOCX
- XLSX
- PPTX
- PDF
- EPUB

Integration complexity strongly favored Tika:

- Tika wrapper: **13** non-comment source lines, **0** format-dispatch branches.
- Python baseline: **60** non-comment source lines, **10** format-dispatch branches.
- Tika used about **21.7%** as many integration lines.

But the preregistered one-fresh-JVM-per-file runtime threshold failed by a very large margin:

- Tika cold full-corpus: **11.987 s**
- Tika second full-corpus: **10.912 s**
- Python cold full-corpus: **0.02322 s**
- Python second full-corpus: **0.01663 s**
- second-run ratio: **656.2×**
- cold-run ratio: **516.2×**

The preregistration required Tika to be **<10×** the Python baseline on this tiny corpus after tool/JVM startup was included.

## Preregistered threshold evaluation

1. Coverage or integration-code advantage: **PASS** — coverage tied 10/10 and Tika used 13 vs 60 integration lines.
2. No per-format Tika dispatch: **PASS** — 0 dispatch branches.
3. Runtime <10× Python: **FAIL** — approximately 656.2× on the second run.

Because all three were required, the Tika claim is **not upgraded**.

The weakening condition also does not hold: although Python was vastly faster for this boundary shape, Python required substantially more format-specific integration code and 10 dispatch branches.

## Interpretation

The experiment supports a narrower boundary rule:

> Apache Tika is strongly attractive when heterogeneous-format coverage would otherwise require a host-language parser matrix, but **do not invoke a fresh JVM/Tika process per tiny file** when latency matters.

The obvious architectural implication is to amortize the JVM boundary:

- use Tika Server / a persistent worker;
- batch files through a warm process;
- keep a JVM subsystem alive;
- or use host-native parsers when the format set is narrow and latency dominates.

This experiment does **not** test a persistent Tika server or batched JVM boundary, so it does not establish their runtime cost.

## Environment

- Apache Tika 3.3.3
- openjdk version "21.0.12.1" 2026-08-18 LTS
- Python 3.13.16
- Linux-6.17.0-1022-azure-x86_64-with-glibc2.39
- Tika app JAR SHA-256: `f29d4e0d2cff1fc32396f6ac5ce436dfc7b19f9303d3b899e1f56fde85711c96`

See `results.json` for the per-file outcomes and exact raw measurements.
