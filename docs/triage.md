# Subsystem triage atlas

> Generated from `registry/registry.json` by `scripts/generate_triage.py`. Do not edit generated sections by hand.

Start with the implementation smell you recognize, then follow the branch toward a specialist candidate. The amber guidance node explains why the crossing may pay and the first strong reason not to cross. Green system nodes are shared terminals, so multiple smells can converge on one specialist.

## Decision DAG

```mermaid
flowchart LR
  root(["What kind of machinery are you about to reinvent?"])
  family_analysis["Analysis"]
  root --> family_analysis
  family_build["Build"]
  root --> family_build
  family_code_analysis["Code Analysis"]
  root --> family_code_analysis
  family_configuration["Configuration"]
  root --> family_configuration
  family_constraints["Constraints"]
  root --> family_constraints
  family_data_transformation["Data Transformation"]
  root --> family_data_transformation
  family_documents["Documents"]
  root --> family_documents
  family_extensibility["Extensibility"]
  root --> family_extensibility
  family_geospatial["Geospatial"]
  root --> family_geospatial
  family_hardware["Hardware"]
  root --> family_hardware
  family_mathematics["Mathematics"]
  root --> family_mathematics
  family_media["Media"]
  root --> family_media
  family_numerics["Numerics"]
  root --> family_numerics
  family_policy["Policy"]
  root --> family_policy
  family_programming_languages["Programming Languages"]
  root --> family_programming_languages
  family_search["Search"]
  root --> family_search
  family_verification["Verification"]
  root --> family_verification
  trigger_analysis_fixed_point_propagation["I have a work queue that propagates facts until nothing changes."]
  family_analysis --> trigger_analysis_fixed_point_propagation
  guide_rec_souffle_fixed_point["Soufflé<br/>very-strong · file-cli<br/>Why: Turns recursive fixed-point propagation into declarative Datalog and supplies optimized evaluation/index…<br/>Avoid if: Execution order and side effects are central to correctness."]
  trigger_analysis_fixed_point_propagation --> guide_rec_souffle_fixed_point
  system_souffle(["Soufflé<br/>dsl"])
  guide_rec_souffle_fixed_point --> system_souffle
  trigger_build_reproducible_closure["Environment and toolchain drift has become part of the bug surface."]
  family_build --> trigger_build_reproducible_closure
  guide_rec_nix_reproducible["Nix<br/>strong · spec-artifact<br/>Why: Makes the dependency/toolchain closure explicit enough to reproduce complex environments rather than rel…<br/>Avoid if: A lockfile plus container already provides adequate reproducibility."]
  trigger_build_reproducible_closure --> guide_rec_nix_reproducible
  system_nix(["Nix<br/>toolchain"])
  guide_rec_nix_reproducible --> system_nix
  trigger_code_csharp_semantics["I need to know what C# code means, not merely how it parses."]
  family_code_analysis --> trigger_code_csharp_semantics
  guide_rec_roslyn_csharp_semantics["Roslyn<br/>extremely-strong · process-rpc<br/>Why: Uses the compiler's own semantic model for binding, symbols, overload resolution, diagnostics, and trans…<br/>Avoid if: Only concrete syntax is needed."]
  trigger_code_csharp_semantics --> guide_rec_roslyn_csharp_semantics
  system_roslyn(["Roslyn<br/>compiler"])
  guide_rec_roslyn_csharp_semantics --> system_roslyn
  trigger_code_incremental_syntax["I need syntax trees while source is incomplete, malformed, or changing interactively."]
  family_code_analysis --> trigger_code_incremental_syntax
  guide_rec_tree_sitter_incremental_syntax["Tree-sitter<br/>extremely-strong · library-ffi<br/>Why: Provides incremental, error-tolerant syntax trees across many languages and is designed for interactive…<br/>Avoid if: Compiler-faithful symbol binding or type semantics are required."]
  trigger_code_incremental_syntax --> guide_rec_tree_sitter_incremental_syntax
  system_tree_sitter(["Tree-sitter<br/>library"])
  guide_rec_tree_sitter_incremental_syntax --> system_tree_sitter
  trigger_config_schema_defaults_overlays["Configuration is turning into schema + defaults + overlays + custom validation code."]
  family_configuration --> trigger_config_schema_defaults_overlays
  guide_rec_cue_config_constraints["CUE<br/>very-strong · file-cli<br/>Why: Collapses values, schemas, defaults, validation, and composition into one constraint/unification represe…<br/>Avoid if: Configuration is flat, static, and already well-served by a conventional schema."]
  trigger_config_schema_defaults_overlays --> guide_rec_cue_config_constraints
  system_cue(["CUE<br/>dsl"])
  guide_rec_cue_config_constraints --> system_cue
  trigger_constraints_answer_set_worlds["I am generating candidate worlds under defaults, exclusions, and combinatorial rules."]
  family_constraints --> trigger_constraints_answer_set_worlds
  guide_rec_clingo_asp["clingo<br/>very-strong · file-cli<br/>Why: Represents combinatorial admissible-world search with defaults and exceptions directly, replacing hand-c…<br/>Avoid if: The logic is monotone recursive closure better expressed as Datalog."]
  trigger_constraints_answer_set_worlds --> guide_rec_clingo_asp
  system_clingo(["clingo<br/>solver"])
  guide_rec_clingo_asp --> system_clingo
  trigger_constraints_relational_partial_terms["I keep writing recursive search where arguments may be known in either direction."]
  family_constraints --> trigger_constraints_relational_partial_terms
  guide_rec_prolog_relational["SWI-Prolog<br/>strong · process-rpc<br/>Why: Turns recursive search and bidirectional relations into direct language semantics through unification, b…<br/>Avoid if: The computation is a large monotone fixed point better suited to Datalog."]
  trigger_constraints_relational_partial_terms --> guide_rec_prolog_relational
  system_swi_prolog(["SWI-Prolog<br/>language"])
  guide_rec_prolog_relational --> system_swi_prolog
  trigger_constraints_smt_theories["I am hand-writing search over arithmetic, bit-vectors, arrays, or logical constraints."]
  family_constraints --> trigger_constraints_smt_theories
  guide_rec_cvc5_smt["cvc5<br/>strong · process-rpc<br/>Why: Offers an independent modern SMT implementation with broad theory support, useful both as a primary solv…<br/>Avoid if: Z3 already satisfies the workload and independent validation has no value."]
  trigger_constraints_smt_theories --> guide_rec_cvc5_smt
  system_cvc5(["cvc5<br/>solver"])
  guide_rec_cvc5_smt --> system_cvc5
  guide_rec_z3_smt["Z3<br/>very-strong · process-rpc<br/>Why: Replaces custom logical search with mature SMT theory reasoning and propagation across mixed Boolean/ari…<br/>Avoid if: Constraint programming globals/scheduling are the natural abstraction."]
  trigger_constraints_smt_theories --> guide_rec_z3_smt
  system_z3(["Z3<br/>solver"])
  guide_rec_z3_smt --> system_z3
  trigger_constraints_solver_independent_cp["I want to model scheduling/allocation constraints without committing to one solver API."]
  family_constraints --> trigger_constraints_solver_independent_cp
  guide_rec_minizinc_cp["MiniZinc<br/>very-strong · spec-artifact<br/>Why: Separates a high-level constraint model from solver choice, avoiding solver-specific imperative search c…<br/>Avoid if: Solver-specific APIs/features are the core requirement."]
  trigger_constraints_solver_independent_cp --> guide_rec_minizinc_cp
  system_minizinc(["MiniZinc<br/>dsl"])
  guide_rec_minizinc_cp --> system_minizinc
  trigger_data_json_pipeline["I need a small program just to reshape JSON in a pipeline."]
  family_data_transformation --> trigger_data_json_pipeline
  guide_rec_jq_json["jq<br/>strong · file-cli<br/>Why: The representation matches the problem directly and crossing cost is effectively zero in pipeline-orient…<br/>Avoid if: The transformation needs substantial application state, I/O orchestration, or d…"]
  trigger_data_json_pipeline --> guide_rec_jq_json
  system_jq(["jq<br/>dsl"])
  guide_rec_jq_json --> system_jq
  trigger_documents_format_conversion["I am writing pairwise converters among documentation and publishing formats."]
  family_documents --> trigger_documents_format_conversion
  guide_rec_pandoc_format_conversion["Pandoc<br/>extremely-strong · file-cli<br/>Why: Normalizes many structured document dialects through a common document AST, avoiding a matrix of pairwis…<br/>Avoid if: Required conversion fidelity is outside Pandoc's supported semantics."]
  trigger_documents_format_conversion --> guide_rec_pandoc_format_conversion
  system_pandoc(["Pandoc<br/>executable"])
  guide_rec_pandoc_format_conversion --> system_pandoc
  trigger_documents_heterogeneous_extraction["I am accumulating one parser per incoming file type."]
  family_documents --> trigger_documents_heterogeneous_extraction
  guide_rec_tika_heterogeneous_extraction["Apache Tika<br/>extremely-strong · process-rpc<br/>Why: Deletes a large parser-integration subsystem by presenting broad document detection, text extraction, an…<br/>Avoid if: The corpus is one narrow well-supported format."]
  trigger_documents_heterogeneous_extraction --> guide_rec_tika_heterogeneous_extraction
  system_apache_tika(["Apache Tika<br/>library"])
  guide_rec_tika_heterogeneous_extraction --> system_apache_tika
  trigger_extensibility_embedded_scripting["My application needs a user/plugin scripting language and I am about to invent one."]
  family_extensibility --> trigger_extensibility_embedded_scripting
  guide_rec_lua_embedding["Lua<br/>very-strong · embedded-runtime<br/>Why: Provides a purpose-built small embeddable language/runtime instead of inventing a bespoke extension DSL…<br/>Avoid if: Users specifically need the Python/JavaScript package ecosystem."]
  trigger_extensibility_embedded_scripting --> guide_rec_lua_embedding
  system_lua(["Lua<br/>language"])
  guide_rec_lua_embedding --> system_lua
  trigger_geo_format_reproject["I am writing geospatial format and coordinate-system plumbing."]
  family_geospatial --> trigger_geo_format_reproject
  guide_rec_gdal_geo["GDAL<br/>extremely-strong · file-cli<br/>Why: Owns a vast portion of geospatial format and coordinate-system plumbing that is expensive and error-pron…<br/>Avoid if: The data has no geospatial coordinate semantics."]
  trigger_geo_format_reproject --> guide_rec_gdal_geo
  system_gdal(["GDAL<br/>library"])
  guide_rec_gdal_geo --> system_gdal
  trigger_hardware_executable_rtl["I want software-style fast tests or fuzzing over Verilog/SystemVerilog RTL."]
  family_hardware --> trigger_hardware_executable_rtl
  guide_rec_verilator_rtl["Verilator<br/>very-strong · generated-artifact<br/>Why: Turns RTL into fast native executable models, enabling ordinary software CI, fuzzing, and differential-t…<br/>Avoid if: Analog/mixed-signal behavior dominates."]
  trigger_hardware_executable_rtl --> guide_rec_verilator_rtl
  system_verilator(["Verilator<br/>compiler"])
  guide_rec_verilator_rtl --> system_verilator
  trigger_math_symbolic_exact_oracle["I need an independently implemented exact/symbolic mathematical oracle."]
  family_mathematics --> trigger_math_symbolic_exact_oracle
  guide_rec_wolfram_symbolic["Wolfram Engine<br/>very-strong · process-rpc<br/>Why: Supplies a very broad independently implemented CAS surface for exact/symbolic reference computation and…<br/>Avoid if: Open-source symbolic tooling already covers the required mathematics."]
  trigger_math_symbolic_exact_oracle --> guide_rec_wolfram_symbolic
  system_wolfram_engine(["Wolfram Engine<br/>runtime"])
  guide_rec_wolfram_symbolic --> system_wolfram_engine
  trigger_media_transcode_filter["I am starting to write codec/container/transcoding glue."]
  family_media --> trigger_media_transcode_filter
  guide_rec_ffmpeg_media["FFmpeg<br/>extremely-strong · file-cli<br/>Why: Deletes broad codec/container/filtering integration by concentrating decades of media interoperability b…<br/>Avoid if: A single platform-native media API completely owns the narrow requirement."]
  trigger_media_transcode_filter --> guide_rec_ffmpeg_media
  system_ffmpeg(["FFmpeg<br/>executable"])
  guide_rec_ffmpeg_media --> system_ffmpeg
  trigger_numerics_compositional_math_types["My custom mathematical objects keep falling out of the numerical stack."]
  family_numerics --> trigger_numerics_compositional_math_types
  guide_rec_julia_compositional_numerics["Julia / SciML / Symbolics<br/>very-strong · subsystem-language<br/>Why: Lets unusual mathematical representations participate generically across symbolic transforms, AD, solver…<br/>Avoid if: The task is routine dataframe/scientific analysis already well-served by Python…"]
  trigger_numerics_compositional_math_types --> guide_rec_julia_compositional_numerics
  system_julia_sciml(["Julia / SciML / Symbolics<br/>platform"])
  guide_rec_julia_compositional_numerics --> system_julia_sciml
  trigger_policy_shared_enforcement["The same policy logic is being reimplemented at several enforcement points."]
  family_policy --> trigger_policy_shared_enforcement
  guide_rec_opa_shared_policy["OPA / Rego<br/>very-strong · process-rpc<br/>Why: Centralizes declarative policy semantics across heterogeneous enforcement points instead of duplicating…<br/>Avoid if: The policy is tiny, local, and inseparable from one application's workflow."]
  trigger_policy_shared_enforcement --> guide_rec_opa_shared_policy
  system_opa_rego(["OPA / Rego<br/>dsl"])
  guide_rec_opa_shared_policy --> system_opa_rego
  trigger_pl_executable_semantics["I am writing a programming-language semantics on paper and a separate interpreter to test it."]
  family_programming_languages --> trigger_pl_executable_semantics
  guide_rec_redex_semantics["Racket / Redex<br/>extremely-strong · spec-artifact<br/>Why: Makes the formal operational semantics itself executable, testable, and generative rather than maintaini…<br/>Avoid if: The goal is production compiler implementation rather than semantic modeling."]
  trigger_pl_executable_semantics --> guide_rec_redex_semantics
  system_racket_redex(["Racket / Redex<br/>library"])
  guide_rec_redex_semantics --> system_racket_redex
  trigger_search_embedded_fulltext["I am building a serious local search engine inside an application."]
  family_search --> trigger_search_embedded_fulltext
  guide_rec_lucene_embedded_fulltext["Apache Lucene<br/>very-strong · library-ffi<br/>Why: Provides a mature embedded search engine without requiring a separate search service or rebuilding index…<br/>Avoid if: Search needs are limited to simple exact lookup or basic database FTS."]
  trigger_search_embedded_fulltext --> guide_rec_lucene_embedded_fulltext
  system_apache_lucene(["Apache Lucene<br/>library"])
  guide_rec_lucene_embedded_fulltext --> system_apache_lucene
  trigger_verification_code_contracts["The proof obligation belongs directly beside executable implementation code."]
  family_verification --> trigger_verification_code_contracts
  guide_rec_dafny_contracts["Dafny<br/>very-strong · subsystem-language<br/>Why: Keeps executable code and deductive contracts/invariants together, with automated verification and compi…<br/>Avoid if: A separate behavioral model answers the real question more cheaply."]
  trigger_verification_code_contracts --> guide_rec_dafny_contracts
  system_dafny(["Dafny<br/>language"])
  guide_rec_dafny_contracts --> system_dafny
  trigger_verification_concurrent_behavior["The bug I fear is some legal interleaving of retries, messages, failover, or concurrent steps."]
  family_verification --> trigger_verification_concurrent_behavior
  guide_rec_tla_concurrent["TLA+ / PlusCal / TLC<br/>very-strong · spec-artifact<br/>Why: Explores nondeterministic state-machine behaviors before implementation details hide the concurrency str…<br/>Avoid if: The main correctness question is static/structural rather than behavioral."]
  trigger_verification_concurrent_behavior --> guide_rec_tla_concurrent
  system_tla_plus(["TLA+ / PlusCal / TLC<br/>model-checker"])
  guide_rec_tla_concurrent --> system_tla_plus
  trigger_verification_machine_proof["Testing or bounded search is insufficient; I need a machine-checked proof."]
  family_verification --> trigger_verification_machine_proof
  guide_rec_lean_proof["Lean 4<br/>strong · spec-artifact<br/>Why: Provides a trusted-kernel machine-checked proof environment when tests, bounded search, and SMT are not…<br/>Avoid if: The assurance requirement does not justify formalization cost."]
  trigger_verification_machine_proof --> guide_rec_lean_proof
  system_lean(["Lean 4<br/>prover"])
  guide_rec_lean_proof --> system_lean
  trigger_verification_relational_counterexample["I want a tiny concrete counterexample to a structural invariant."]
  family_verification --> trigger_verification_relational_counterexample
  guide_rec_alloy_relational["Alloy<br/>very-strong · spec-artifact<br/>Why: Expresses finite relational structure compactly and searches for small concrete counterexamples to invar…<br/>Avoid if: Absence of a bounded counterexample must constitute an unbounded proof."]
  trigger_verification_relational_counterexample --> guide_rec_alloy_relational
  system_alloy(["Alloy<br/>model-checker"])
  guide_rec_alloy_relational --> system_alloy

  classDef root fill:#111827,color:#ffffff,stroke:#111827,stroke-width:2px;
  classDef family fill:#e0f2fe,color:#0c4a6e,stroke:#0284c7,stroke-width:1px;
  classDef trigger fill:#f8fafc,color:#0f172a,stroke:#64748b,stroke-width:1px;
  classDef guide fill:#fef3c7,color:#78350f,stroke:#d97706,stroke-width:1px;
  classDef system fill:#dcfce7,color:#14532d,stroke:#16a34a,stroke-width:2px;
  class root root;
  class family_analysis,family_build,family_code_analysis,family_configuration,family_constraints,family_data_transformation,family_documents,family_extensibility,family_geospatial,family_hardware,family_mathematics,family_media,family_numerics,family_policy,family_programming_languages,family_search,family_verification family;
  class trigger_documents_heterogeneous_extraction,trigger_analysis_fixed_point_propagation,trigger_code_csharp_semantics,trigger_code_incremental_syntax,trigger_config_schema_defaults_overlays,trigger_documents_format_conversion,trigger_search_embedded_fulltext,trigger_media_transcode_filter,trigger_geo_format_reproject,trigger_data_json_pipeline,trigger_policy_shared_enforcement,trigger_pl_executable_semantics,trigger_constraints_smt_theories,trigger_constraints_solver_independent_cp,trigger_constraints_answer_set_worlds,trigger_constraints_relational_partial_terms,trigger_verification_concurrent_behavior,trigger_verification_relational_counterexample,trigger_verification_code_contracts,trigger_verification_machine_proof,trigger_numerics_compositional_math_types,trigger_math_symbolic_exact_oracle,trigger_build_reproducible_closure,trigger_extensibility_embedded_scripting,trigger_hardware_executable_rtl trigger;
  class guide_rec_tika_heterogeneous_extraction,guide_rec_souffle_fixed_point,guide_rec_roslyn_csharp_semantics,guide_rec_tree_sitter_incremental_syntax,guide_rec_cue_config_constraints,guide_rec_pandoc_format_conversion,guide_rec_lucene_embedded_fulltext,guide_rec_ffmpeg_media,guide_rec_gdal_geo,guide_rec_jq_json,guide_rec_opa_shared_policy,guide_rec_redex_semantics,guide_rec_z3_smt,guide_rec_cvc5_smt,guide_rec_minizinc_cp,guide_rec_clingo_asp,guide_rec_prolog_relational,guide_rec_tla_concurrent,guide_rec_alloy_relational,guide_rec_dafny_contracts,guide_rec_lean_proof,guide_rec_julia_compositional_numerics,guide_rec_wolfram_symbolic,guide_rec_nix_reproducible,guide_rec_lua_embedding,guide_rec_verilator_rtl guide;
  class system_alloy,system_apache_lucene,system_apache_tika,system_clingo,system_cue,system_cvc5,system_dafny,system_ffmpeg,system_gdal,system_jq,system_julia_sciml,system_lean,system_lua,system_minizinc,system_nix,system_opa_rego,system_pandoc,system_racket_redex,system_roslyn,system_souffle,system_swi_prolog,system_tla_plus,system_tree_sitter,system_verilator,system_wolfram_engine,system_z3 system;
```

## Readable decision table

| Family | Implementation smell | Candidate | Why consider it | Avoid when | Cheapest boundary |
| --- | --- | --- | --- | --- | --- |
| Analysis | I have a work queue that propagates facts until nothing changes. | Soufflé | Turns recursive fixed-point propagation into declarative Datalog and supplies optimized evaluation/indexing machinery instead of hand-maintained worklists. | Execution order and side effects are central to correctness.; The workload is dominated by numerical kernels rather than relations. | file-cli — facts in / relations out, or compile to a generated executable |
| Build | Environment and toolchain drift has become part of the bug surface. | Nix | Makes the dependency/toolchain closure explicit enough to reproduce complex environments rather than relying on ambient machine state. | A lockfile plus container already provides adequate reproducibility.; The organization cannot justify Nix's substantial conceptual learning cost. | spec-artifact — nix develop/build wrapped around the existing project |
| Code Analysis | I need syntax trees while source is incomplete, malformed, or changing interactively. | Tree-sitter | Provides incremental, error-tolerant syntax trees across many languages and is designed for interactive source that may not currently compile. | Compiler-faithful symbol binding or type semantics are required. | library-ffi — native or Wasm binding |
| Code Analysis | I need to know what C# code means, not merely how it parses. | Roslyn | Uses the compiler's own semantic model for binding, symbols, overload resolution, diagnostics, and transformations instead of approximating C# meaning. | Only concrete syntax is needed.; The target language is outside Roslyn's compiler surface. | process-rpc — small .NET worker or direct library when the host is already .NET |
| Configuration | Configuration is turning into schema + defaults + overlays + custom validation code. | CUE | Collapses values, schemas, defaults, validation, and composition into one constraint/unification representation. | Configuration is flat, static, and already well-served by a conventional schema.; Introducing a new DSL costs more than the duplicated validation logic. | file-cli — cue vet/export at build or configuration-generation time |
| Constraints | I am generating candidate worlds under defaults, exclusions, and combinatorial rules. | clingo | Represents combinatorial admissible-world search with defaults and exceptions directly, replacing hand-coded candidate generation/backtracking. | The logic is monotone recursive closure better expressed as Datalog.; The task is primarily continuous/numeric optimization. | file-cli — facts/rules in, stable models out; API when incremental solving is needed |
| Constraints | I am hand-writing search over arithmetic, bit-vectors, arrays, or logical constraints. | cvc5 | Offers an independent modern SMT implementation with broad theory support, useful both as a primary solver and as a cross-checking oracle. | Z3 already satisfies the workload and independent validation has no value.; The problem maps more naturally to CP or ASP. | process-rpc — SMT-LIB process |
| Constraints | I am hand-writing search over arithmetic, bit-vectors, arrays, or logical constraints. | Z3 | Replaces custom logical search with mature SMT theory reasoning and propagation across mixed Boolean/arithmetic/bit-vector structures. | Constraint programming globals/scheduling are the natural abstraction.; The problem is primarily nonmonotonic defaults/exceptions. | process-rpc — SMT-LIB process or host API |
| Constraints | I keep writing recursive search where arguments may be known in either direction. | SWI-Prolog | Turns recursive search and bidirectional relations into direct language semantics through unification, backtracking, and CLP libraries. | The computation is a large monotone fixed point better suited to Datalog.; The relation is trivial enough that adding a runtime outweighs the modeling benefit. | process-rpc — separate Prolog process/Pengine or subsystem module |
| Constraints | I want to model scheduling/allocation constraints without committing to one solver API. | MiniZinc | Separates a high-level constraint model from solver choice, avoiding solver-specific imperative search code. | Solver-specific APIs/features are the core requirement.; The problem maps directly to SMT theories with no benefit from CP globals. | spec-artifact — .mzn model plus CLI/API |
| Data Transformation | I need a small program just to reshape JSON in a pipeline. | jq | The representation matches the problem directly and crossing cost is effectively zero in pipeline-oriented JSON work. | The transformation needs substantial application state, I/O orchestration, or domain behavior.; The team cannot accept a separate command-line dependency. | file-cli — stdin/stdout |
| Documents | I am accumulating one parser per incoming file type. | Apache Tika | Deletes a large parser-integration subsystem by presenting broad document detection, text extraction, and metadata normalization behind one surface. | The corpus is one narrow well-supported format.; Exact page geometry or rendering fidelity is the actual product requirement. | process-rpc — Tika app/server or a tiny JBang/JVM wrapper |
| Documents | I am writing pairwise converters among documentation and publishing formats. | Pandoc | Normalizes many structured document dialects through a common document AST, avoiding a matrix of pairwise converters. | Required conversion fidelity is outside Pandoc's supported semantics.; The problem is extraction from arbitrary binary formats rather than structured conversion. | file-cli — pandoc executable with files/stdin/stdout |
| Extensibility | My application needs a user/plugin scripting language and I am about to invent one. | Lua | Provides a purpose-built small embeddable language/runtime instead of inventing a bespoke extension DSL or embedding a much heavier general runtime. | Users specifically need the Python/JavaScript package ecosystem.; The application does not actually need runtime scripting. | embedded-runtime — Lua VM embedded through C API/FFI |
| Geospatial | I am writing geospatial format and coordinate-system plumbing. | GDAL | Owns a vast portion of geospatial format and coordinate-system plumbing that is expensive and error-prone to recreate. | The data has no geospatial coordinate semantics.; The task is a narrow operation fully supported by an existing host GIS API. | file-cli — gdal* CLI first; bindings when repeated in-process calls justify them |
| Hardware | I want software-style fast tests or fuzzing over Verilog/SystemVerilog RTL. | Verilator | Turns RTL into fast native executable models, enabling ordinary software CI, fuzzing, and differential-test techniques over hardware designs. | Analog/mixed-signal behavior dominates.; Required simulation semantics rely on constructs outside Verilator's intended model. | generated-artifact — generated C++/SystemC executable model |
| Mathematics | I need an independently implemented exact/symbolic mathematical oracle. | Wolfram Engine | Supplies a very broad independently implemented CAS surface for exact/symbolic reference computation and differential testing. | Open-source symbolic tooling already covers the required mathematics.; Production licensing or authentication constraints outweigh the coverage advantage. | process-rpc — wolframscript/local Wolfram Engine |
| Media | I am starting to write codec/container/transcoding glue. | FFmpeg | Deletes broad codec/container/filtering integration by concentrating decades of media interoperability behind a CLI/library surface. | A single platform-native media API completely owns the narrow requirement.; Licensing obligations of the selected FFmpeg build are incompatible with deployment. | file-cli — ffprobe/ffmpeg subprocess |
| Numerics | My custom mathematical objects keep falling out of the numerical stack. | Julia / SciML / Symbolics | Lets unusual mathematical representations participate generically across symbolic transforms, AD, solvers, optimization, and native specialization. | The task is routine dataframe/scientific analysis already well-served by Python/R.; Only standard numeric kernels are needed and mature host libraries already dominate. | subsystem-language — Julia numerical subsystem or worker process |
| Policy | The same policy logic is being reimplemented at several enforcement points. | OPA / Rego | Centralizes declarative policy semantics across heterogeneous enforcement points instead of duplicating policy code per service. | The policy is tiny, local, and inseparable from one application's workflow.; An existing platform policy engine already owns all enforcement points. | process-rpc — local OPA process/REST or embedded evaluator |
| Programming Languages | I am writing a programming-language semantics on paper and a separate interpreter to test it. | Racket / Redex | Makes the formal operational semantics itself executable, testable, and generative rather than maintaining a paper model plus a separate interpreter. | The goal is production compiler implementation rather than semantic modeling.; Only parsing or AST manipulation is needed. | spec-artifact — standalone Racket/Redex model and test suite |
| Search | I am building a serious local search engine inside an application. | Apache Lucene | Provides a mature embedded search engine without requiring a separate search service or rebuilding indexing/ranking/query infrastructure. | Search needs are limited to simple exact lookup or basic database FTS.; Operational requirements already favor a dedicated external search cluster. | library-ffi — JVM library or thin local service |
| Verification | I want a tiny concrete counterexample to a structural invariant. | Alloy | Expresses finite relational structure compactly and searches for small concrete counterexamples to invariants. | Absence of a bounded counterexample must constitute an unbounded proof.; Temporal behavior rather than structure is the main concern. | spec-artifact — Alloy model plus analyzer/model finder |
| Verification | Testing or bounded search is insufficient; I need a machine-checked proof. | Lean 4 | Provides a trusted-kernel machine-checked proof environment when tests, bounded search, and SMT are not sufficient evidence. | The assurance requirement does not justify formalization cost.; The property is better handled automatically by SMT/model checking. | spec-artifact — separate Lean proof project checked in CI |
| Verification | The bug I fear is some legal interleaving of retries, messages, failover, or concurrent steps. | TLA+ / PlusCal / TLC | Explores nondeterministic state-machine behaviors before implementation details hide the concurrency structure, producing concrete counterexample traces. | The main correctness question is static/structural rather than behavioral.; The model cannot be kept meaningfully aligned with the implementation. | spec-artifact — .tla/.cfg model checked in CI |
| Verification | The proof obligation belongs directly beside executable implementation code. | Dafny | Keeps executable code and deductive contracts/invariants together, with automated verification and compilation to mainstream targets. | A separate behavioral model answers the real question more cheaply.; The proof requires deep interactive mathematics beyond Dafny's intended workflow. | subsystem-language — verified critical module compiled/exported into the host system |

## Design constraints

- This is a DAG, not a forced tree: shared terminal systems preserve convergence.
- Guidance is recommendation-edge data, not duplicated system metadata.
- Every recommendation has explicit negative discrimination through `avoid_when`.
- The diagram and table are generated from the same canonical registry consumed by the future CLI.
