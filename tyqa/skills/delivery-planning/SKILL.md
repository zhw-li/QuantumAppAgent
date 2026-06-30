---
name: delivery-planning
description: "Guides detailed planning for a selected quantum application route: application_manifest.json, requirements.json, baseline plan, quantum algorithm route, delivery_profile, validation gates, artifact paths, qccp/local packaging boundaries, and acceptance criteria. Use when a route has been selected and the user needs an implementation-ready plan. Do NOT use for open-ended intake (use application-intake), broad method evidence maps (use solution-landscape), execution/debugging (use application-pipeline or application-debugging), or final docs (use delivery-writing)."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, delivery-planning, manifest, validation]
---

# Delivery Planning

Turn a selected quantum application route into an implementation-ready contract. This skill owns the plan before execution; `application-pipeline` owns staged implementation and validation.

## When to Use This Skill

- User has selected a route from `application-intake` or `solution-landscape`.
- User needs `application_manifest.json`, `requirements.json`, `solution_plan.md`, `algorithm_route.md`, or `validation_plan.md` drafted or refined.
- User needs to choose a `delivery_profile` and define what counts as acceptance.
- User wants a baseline-first implementation plan before Cqlib/qccp work begins.
- User asks what artifacts, commands, metrics, and handoff materials the PoC must produce.

## When NOT to Use

- Open-ended requirements conversation -> use `application-intake`.
- Evidence discovery or method landscape -> use `evidence-navigator` / `solution-landscape`.
- Running code, tests, or qccp packaging -> use `application-pipeline` and downstream implementation skills.
- Debugging an active failure -> use `application-debugging`.
- Writing final README, INTEGRATE, reports, or slides -> use `delivery-writing` / `showcase-slides`.

## Planning Overview

Produce a plan that can be executed without reinterpreting the user's intent:

1. Define the application contract.
2. Define baseline and quantum comparison.
3. Define artifact paths and validation commands.
4. Define packaging boundaries by `delivery_profile`.
5. Define acceptance criteria and known blockers.

Do not assume a fixed artifact directory. Use the caller-provided or current project artifact location and record the actual paths.

## Step 1: Application Contract

Create or update `application_manifest.json` with:

- `application_name`
- `task_type`
- `delivery_profile`
- `inputs` and `outputs`
- `primary_metric` and `higher_is_better`
- `algorithm` route
- `baseline_report` path
- `quantum_report` path
- `local_demo` contract if in scope
- `qccp_web` contract if in scope
- `docs` and handoff artifacts
- validation commands
- limitations and unresolved assumptions

Create or update `requirements.json` with the same user-facing requirements in a machine-checkable form.

## Step 2: Baseline Plan

Define the classical comparator before the quantum method:

- baseline algorithm or implementation
- data source and split
- metric and expected output schema
- command to run the baseline
- report schema for `baseline_report.json`
- minimum acceptable reproducibility evidence

If the baseline is weak or missing, mark it as a blocker. Do not proceed to quantum claims without a comparator.

## Step 3: Quantum Route Plan

Define the route in implementation terms:

- encoding or QUBO/Hamiltonian construction
- ansatz/objective/observable
- optimizer and seeds
- backend (`simulator`, authorized cloud, or real hardware)
- shots and noise assumptions when relevant
- result schema for `quantum_report.json`
- how the result will be compared to `baseline_report.json`

Route through the Cqlib skills:

| Route | Skill path |
|-------|------------|
| QUBO/QAOA/optimization | `cqlib-sdk` + `cqlib-qaoa` |
| VQE/Hamiltonian/chemistry | `cqlib-sdk` + `cqlib-vqe` |
| VQC/QML | `cqlib-sdk` + `cqlib-qml` |
| Hybrid neural model | `cqlib-sdk` + `cqlib-hybrid` |

## Step 4: Delivery Profile Plan

Select one profile and state why:

- `algorithm_only`: algorithm artifacts and validation reports only.
- `local_fastapi_demo`: add local API/demo contract through `qccp-service`.
- `qccp_web_page`: add qccp-web page contract through `qccp-ui` and `qccp-frontend`.
- `full_delivery`: include algorithm, local demo, qccp page, docs, and showcase materials.

For each in-scope layer, define:

- source/output paths
- required commands
- expected review evidence
- explicit out-of-scope layers

## Step 5: Validation Plan

Draft `validation_plan.md` with:

- artifact existence checks
- baseline-vs-quantum comparability checks
- metric direction and thresholds
- packaging checks by profile
- `validate_quantum_application(app_dir)` command or API call
- claim boundaries for simulator/cloud/hardware
- blockers that must be fixed or reported

## Step 6: Execution Plan

Draft `solution_plan.md` as a staged checklist:

| Stage | Goal | Success signal | Expected artifacts |
|-------|------|----------------|--------------------|
| Baseline | runnable classical reference | `baseline_report.json` exists and matches metric | code, data notes, report |
| Quantum | comparable Cqlib method | `quantum_report.json` comparable to baseline | circuit/model code, report |
| Packaging | selected delivery profile implemented | local/qccp evidence exists or out of scope | API/UI/docs |
| Verification | claims match artifacts | validator and review pass | verification report, README, INTEGRATE |

## Handoff

| Next step | Target skill | Handoff payload |
|-----------|--------------|-----------------|
| Execute staged work | `application-pipeline` | manifest, requirements, solution plan, algorithm route, validation plan |
| Implement quantum method | `cqlib-*` skills | route plan, data contract, metric, backend assumptions |
| Package local/qccp demo | `qccp-service`, `qccp-ui`, `qccp-frontend` | delivery profile contract and API/UI paths |
| Diagnose failure | `application-debugging` | stage, command, observed failure, expected gate |
| Write docs/deck | `delivery-writing`, `showcase-slides` | verified artifacts and limitations |

## Reference Navigation

Existing planning references may still be useful as tactical templates:

| Topic | Reference File | Use |
|-------|---------------|-----|
| Route and stage plan | `references/experiment-planning.md` | Translate to application stages |
| Narrative clarity | `references/story-design.md` | Explain the user workflow and route choice |
| Visual explanation | `references/figure-design.md` | Diagram algorithm/data/app flow |
| Timeline | `references/timeline-4week.md` | Delivery scheduling |
| Plan template | `assets/experiment-plan-template.md` | Optional scaffold |
