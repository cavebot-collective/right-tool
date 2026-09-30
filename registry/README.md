# Registry

The registry is the canonical substrate for right-tool. Human-facing diagrams, generated documentation, and CLI lookup should be derived from this data rather than duplicating research claims by hand.

## Files

- `registry.json` — normalized graph data.
- `schema/right-tool-registry.schema.json` — JSON Schema (Draft 2020-12).
- `../scripts/validate_registry.py` — schema plus referential-integrity validation.

## Graph model

The registry deliberately separates four concepts:

- **systems** — specialist tools, languages, DSLs, solvers, runtimes, libraries, etc.
- **triggers** — implementation smells or problem shapes a developer can recognize.
- **recommendations** — many-to-many edges from triggers to systems, carrying the actual crossing-cost judgment.
- **evidence / experiments** — provenance and empirical calibration.

This means one system can be reached through many different human entry points without repeating system metadata, and one trigger can legitimately surface several competing systems.

## Required negative evidence

Every recommendation must include `avoid_when`. right-tool is intended to discriminate, not merely accumulate suggestions.

For example:

- Roslyn is excellent when C# semantics matter, but excessive for syntax-only parsing.
- Tree-sitter is excellent for incremental syntax, but not a substitute for compiler semantic binding.
- Pandoc is usually a CLI borrowing decision, not a reason to adopt Haskell.

## Boundary kinds

Integration depth is explicit and ordered roughly from least to greatest commitment:

1. `file-cli`
2. `process-rpc`
3. `library-ffi`
4. `embedded-runtime`
5. `spec-artifact`
6. `generated-artifact`
7. `subsystem-language`
8. `whole-project`

The ordering is heuristic rather than a universal cost metric; the recommendation records the cheapest sensible boundary for its specific trigger/system pair.

## Validation

Install development requirements and run:

```sh
python -m pip install -r requirements-dev.txt
python scripts/validate_registry.py
```

CI runs the same validation for registry-related changes.
