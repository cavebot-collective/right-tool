# right-tool

**The right tool — or language — for every job.**

Docs, visual decision aids, a machine-readable capability registry, and a CLI that help developers and architects recognize when a specialist ecosystem can eliminate more work than staying stack-pure.

The governing question is:

> **What kind of machinery are you about to reinvent?**

Examples include FFmpeg for media, Tika for heterogeneous documents, Soufflé for recursive fixed-point analysis, Roslyn for C# semantics, Julia/SciML for compositional numerical systems, Lean for machine-checked proofs, and CUE for constraint-oriented configuration.

## Start here

- [Visual atlas](docs/atlas.html)
- [Subsystem triage DAG](docs/triage.md)
- [Project architecture and roadmap](PROJECT.md)
- [Research corpus](research/)
  - [Discovery-first crossing-cost atlas](research/2026-09-25-crossing-cost-advantage-atlas.md)
  - [Programming-language ecosystem override atlas](research/2026-09-25-programming-language-ecosystem-override-atlas.md)

GitHub issues are the active work queue. The registry and generated visualizations will remain source-controlled so the research, decision rules, UI, and CLI share one canonical substrate.

## CLI

The deterministic CLI consumes the same canonical registry as the visual atlas.

```sh
python -m pip install -e .
right-tool find "worklist propagation until convergence"
right-tool find "heterogeneous office pdf email extraction" --json
right-tool show souffle
```

Set `RIGHT_TOOL_REGISTRY` or pass `--registry PATH` to use another compatible registry file.
