# right-tool project plan

## Mission

Build a human- and machine-usable atlas that answers:

> **What kind of machinery are you about to reinvent, and is there a specialist system whose advantage is large enough to justify crossing an ecosystem boundary?**

The unit of analysis is **capability → candidate specialist → asymmetric advantage → cheapest integration boundary**, not "language → list of strengths."

## Core decision rule

Stay in the normal implementation ecosystem until another ecosystem can:

1. delete a subsystem;
2. supply semantics that would otherwise have to be recreated;
3. turn search/algorithmic machinery into a declarative specification;
4. eliminate a material class of correctness risk; or
5. represent the core problem so much better that the crossing cost is clearly repaid.

When crossing is justified, prefer the narrowest stable boundary that captures the advantage:

`CLI/file interchange → process/RPC → library/FFI → embedded runtime → subsystem language → whole-project adoption`.

## Human interface

The primary UI is a **decision DAG / flowchart system**, not a giant language table.

Humans should be able to enter through recognizable implementation smells such as:

- "I am writing a parser."
- "I have a work queue that propagates until convergence."
- "I am layering schema + defaults + validation + overlays."
- "I am generating candidates and backtracking."
- "I am reasoning about interleavings/state transitions."
- "I am converting or normalizing specialist formats."
- "I need compiler semantics, not syntax."
- "I am building symbolic/numerical machinery."
- "I need a proof, model finder, solver, policy engine, or embedded extension language."

The graph should then narrow to candidate systems, explain why each candidate applies, and show the cheapest borrowing boundary.

A single huge tree is explicitly **not** the target. The UI should expose multiple shallow views over one reusable graph.

## Canonical data model

The durable source should be machine-readable and capable of generating both docs and visualizations.

Each trigger/candidate relationship should eventually carry:

- `id`
- problem/capability family
- trigger / implementation smell
- positive signals
- candidate system
- system category (language, DSL, solver, prover, executable, library, runtime, etc.)
- asymmetric advantage
- negative discriminators / avoid-when
- closest alternatives
- cheapest integration boundary
- crossing/activation costs
- maturity / maintenance state
- licensing/deployment constraints
- evidence/source references
- confidence
- concrete example
- candidate validation experiment(s)

The schema must allow many-to-many relationships: one smell may lead to several candidates, and one specialist may be reachable from several smells.

## Visual views

The initial human-facing views should be:

1. **Subsystem triage DAG** — "What kind of machinery are you about to reinvent?"
2. **Capability topology** — clustered graph of neighboring specialist systems.
3. **Boundary-depth view** — CLI/process/library/embedding/adoption commitment.
4. **Candidate comparison panel** — saved complexity, correctness gain, integration burden, operational burden, learning cost, and evidence confidence.

## Research corpus

The initial corpus is preserved under `research/`:

- `2026-09-25-programming-language-ecosystem-override-atlas.md` — first language-oriented pass.
- `2026-09-25-crossing-cost-advantage-atlas.md` — second discovery-first, capability-oriented pass.

The second pass is the stronger conceptual basis. The first pass remains useful as a record of hypotheses, counterexamples, and ecosystem-specific discoveries.

## Initial high-confidence nodes

Seed the first structured graph from the strongest researched cases rather than attempting exhaustive coverage immediately:

- Apache Tika
- Apache Lucene
- Pandoc
- FFmpeg
- GDAL
- jq
- CUE
- OPA/Rego
- Roslyn
- Tree-sitter
- Racket/Redex
- Soufflé Datalog
- Z3
- cvc5
- MiniZinc
- clingo
- SWI-Prolog / CLP(FD)
- TLA+ / PlusCal / TLC
- Alloy
- Dafny
- Lean
- Rocq
- Isabelle
- Julia / Symbolics / SciML
- Wolfram Engine
- Nix
- Lua
- Zig
- Verilator
- Chisel / CIRCT
- Stan
- JAX

The initial dataset should include explicit **negative discriminators**. Examples:

- TLA+ ≠ generic "correctness"; it is strongest for state-transition/concurrent behavior.
- Roslyn ≠ generic C# parsing; use it when actual C# semantics/binding matter.
- Tree-sitter ≠ semantic understanding; it is strong for incremental, error-tolerant syntax.
- Wolfram ≠ generic "do math"; it is a broad exact/symbolic oracle.
- Julia ≠ generic "numerics"; the strongest case is compositional mathematical/numerical systems.
- Pandoc ≠ a reason to adopt Haskell; it is usually a specialist executable boundary.

## Delivery phases

### Phase 0 — bootstrap
- Preserve research corpus and provenance.
- Establish canonical plan.
- Create issue-based work queue.

### Phase 1 — registry
- Define machine-readable schema.
- Normalize 20–30 high-confidence specialists and their trigger relationships.
- Add evidence/provenance and negative discriminators.
- Validate schema with generated static documentation.

### Phase 2 — visual decision atlas
- Build the first subsystem-triage DAG.
- Add capability-cluster and boundary-depth views.
- Keep visualization generated from canonical registry data.

### Phase 3 — query interface
- Implement a small CLI that accepts either explicit keywords or a prose problem description.
- Return matched triggers, candidate systems, why/why-not reasoning, and cheapest boundary.
- Preserve deterministic registry lookup independent of any optional LLM-assisted query interpretation.

### Phase 4 — empirical calibration
- Run targeted bake-offs where the claimed crossing advantage is consequential or uncertain.
- Record experimental artifacts and refine trigger thresholds.

## Project management

GitHub issues are the execution queue. This file defines the project-level architecture and decision rules; issues should link back here rather than duplicating those rules.

Keep issues small enough to close with evidence. Research additions should update the registry and provenance rather than living only in issue discussion.
