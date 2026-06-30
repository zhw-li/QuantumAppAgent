---
name: solution-landscape
description: "Guides creation of a quantum application solution landscape: evidence-backed map of algorithms, datasets, baselines, implementation routes, Cqlib/qccp constraints, validation metrics, and delivery risks. Use when the user needs a method/baseline/dataset/platform landscape for a quantum application or PoC before choosing a route. Do NOT use for raw paper discovery (use evidence-navigator), conversational requirement intake and Top-3 route selection (use application-intake), detailed artifact planning (use delivery-planning), or staged execution (use application-pipeline)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, solution-landscape, evidence, baselines]
---

# Solution Landscape

Build an evidence-backed map of practical routes for a quantum algorithm application. The output is not a literature survey by default; it is a decision aid for choosing an implementable route.

## When to Use

- User needs to compare algorithm families, baselines, datasets, metrics, and engineering constraints.
- User has collected papers/repos/dataset notes and wants them converted into application route options.
- User needs defensible evidence before `application-intake` ranks routes or `delivery-planning` writes contracts.
- User asks "what approaches are available", "which baseline is fair", "what data can we use", or "what cloud constraints matter" for a quantum PoC.

## When NOT to Use

- Finding the evidence itself -> use `evidence-navigator`.
- Dialogue-style requirement clarification -> use `application-intake`.
- Planning concrete artifact paths and stage gates -> use `delivery-planning`.
- Implementing or validating the application -> use `application-pipeline`.
- Writing final handoff docs -> use `delivery-writing`.

## Inputs

Accept any combination of:

- User problem statement or draft `application_brief.md`.
- Paper/repo/dataset/baseline notes from `evidence-navigator`.
- Existing `requirements.json`, `application_manifest.json`, or `solution_plan.md` drafts.
- Constraints from Cqlib, qccp, local service packaging, or cloud/hardware usage.

If evidence is insufficient for a claim, mark it as "needs verification" rather than filling gaps from memory.

## Workflow

### Stage 1: Scope the Landscape

Define the decision space:

- task type and target user workflow
- candidate quantum algorithm families
- classical baseline families
- dataset options and access status
- primary metric and metric direction
- delivery profile candidates
- simulator/cloud/hardware boundary

### Stage 2: Build the Method Map

Create a route matrix instead of prose-only synthesis.

| Route family | Best-fit tasks | Data needs | Baseline | Cqlib path | Delivery fit | Key risk |
|--------------|----------------|------------|----------|------------|--------------|----------|
| QAOA/QUBO | Combinatorial optimization | Binary/constraint data | OR-Tools, MILP, greedy | `cqlib-qaoa` | algorithm or qccp demo | QUBO quality |
| VQE | Hamiltonian/chemistry | Hamiltonian terms | exact diagonalization or known reference | `cqlib-vqe` | algorithm demo | observable correctness |
| VQC/QML | classification/regression | labeled tabular/image features | sklearn/torch model | `cqlib-qml` | local/qccp demo | no fair advantage |
| Hybrid neural | sequence/image hybrid | train/test split | classical neural model | `cqlib-hybrid` | full demo possible | training instability |

Add or remove rows based on the actual domain.

### Stage 3: Map Baselines and Data

For every viable route, identify:

- baseline implementation or package
- dataset source and license/access limits
- split policy and leakage risks
- metric and direction
- minimum evidence needed to call the result comparable
- runtime, dependency, and reproducibility requirements

### Stage 4: Map Delivery Constraints

Tie each route to a delivery profile:

- `algorithm_only`: code, reports, validation artifacts.
- `local_fastapi_demo`: FastAPI service, request/response schema, local HTML/static demo.
- `qccp_web_page`: qccp-web Vue page, API contract, route snippet, scoped styles.
- `full_delivery`: algorithm evidence, local demo, qccp page, docs, verification report, and showcase material.

State when a profile is not justified. For example, do not recommend `full_delivery` when the dataset is unavailable or the quantum result cannot be compared.

### Stage 5: Produce the Landscape Report

Recommended output:

```markdown
# Solution Landscape: [application name]

## Decision Summary
[recommended route family and why]

## Candidate Route Matrix
[route table]

## Baseline and Dataset Map
[baseline/data/metric table]

## Cqlib and qccp Implementation Map
[skill routing and package targets]

## Validation Risks
[comparability, metric, data, backend, packaging risks]

## Recommended Next Step
[application-intake, delivery-planning, or application-pipeline]
```

## Handoff

| Next step | Target skill | Payload |
|-----------|--------------|---------|
| Need user route selection | `application-intake` | Route matrix, risks, recommended Top-3 candidates |
| Route already selected | `delivery-planning` | Method map, baseline/data map, delivery constraints |
| Ready to execute | `application-pipeline` | Selected route, baseline, metric, artifacts to create |
| Need more evidence | `evidence-navigator` | Missing paper/repo/dataset/baseline questions |

## Quality Rules

1. Separate algorithm fit from delivery fit.
2. Do not rank by novelty alone; rank by comparable evidence and implementation path.
3. Record unresolved assumptions explicitly.
4. Keep simulator, cloud, and real-hardware claims separate.
5. Do not write customer-facing readiness claims from a landscape alone.

## References

Use existing references only when they help structure a landscape:

| Resource | Use |
|----------|-----|
| `references/survey-methodology.md` | Broad evidence synthesis mechanics |
| `references/section-quality-checklist.md` | Completeness checks for long reports |
| `assets/survey-template.md` | Optional long-form report scaffold |
