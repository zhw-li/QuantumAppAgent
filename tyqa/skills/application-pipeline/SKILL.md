---
name: application-pipeline
description: "Guides staged execution of a quantum algorithm application from baseline to Cqlib quantum method, application packaging, deterministic validation, and handoff. Use when the user has a selected route or plan and needs stage gates, artifact tracking, baseline_report.json, quantum_report.json, application_manifest.json, delivery_profile handling, qccp/local packaging, validate_quantum_application, and delivery docs. Do NOT use for early requirement intake (use application-intake), broad evidence maps (use solution-landscape), or isolated failure diagnosis (use application-debugging)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, pipeline, validation, delivery]
---

# Application Pipeline

A structured 4-stage framework for delivering quantum applications from requirements and baseline through quantum implementation, app packaging, deterministic validation, and handoff. Each stage has a goal, attempt budget, gate condition, artifact trail, and diagnosis path.

## When to Use This Skill

- User has a planned quantum application or PoC and needs to execute it.
- User wants baseline-first validation before making quantum claims.
- User needs Cqlib algorithm evidence, qccp page/API packaging, or cloud showcase readiness.
- User asks about stage gates, attempt budgets, artifact contracts, or when to advance.
- User needs reproducible artifacts for README, INTEGRATE, verification report, or slides.

## When NOT to Use

- Open-ended evidence discovery or route landscape -> use `evidence-navigator` or `solution-landscape`.
- Finding candidate application directions -> use `application-intake`.
- Planning only, before implementation begins -> use `delivery-planning`.
- Standalone frontend/backend artifact generation -> use `qccp-ui`, `qccp-frontend`, or `qccp-service`.
- Prose-only delivery writing or slides -> use `delivery-writing` or `showcase-slides`.

## Pipeline Mindset

Quantum applications fail for two common reasons: unverifiable comparison and unreviewable packaging. A simulator result without a baseline is not evidence, and an algorithm without an API/page/handoff cannot be showcased. The pipeline enforces order, limits unproductive retries, and keeps claims tied to artifacts.

Do not run TianYan/GuoDun hardware jobs unless the user explicitly authorizes the run and provides credentials through environment variables or ignored local config. Simulator results must not be described as real-hardware performance.

## Before Starting

If coming from `application-intake` or `delivery-planning`, use the draft artifacts to define task type, dataset, baseline, primary metric, expected artifacts, and selected `delivery_profile`.

When prior work may help, load `application-memory` and select the top relevant entry for the current application domain. Use it to inform baseline design, encoding/ansatz choices, debugging, packaging, or known qccp constraints. If no relevant memory exists, skip.

## 4-Stage Pipeline Overview

Each stage follows a generate -> execute -> record -> diagnose -> revise loop.

| Stage | Goal | Budget | Gate Condition |
|-------|------|--------|----------------|
| 1. Application Scope & Baseline | Structure requirements and produce a runnable classical baseline | <=10 attempts | Requirements, data, primary metric, `higher_is_better`, and baseline result are explicit and reproducible |
| 2. Quantum Method Implementation | Implement the Cqlib quantum method and compare against the baseline | <=12 attempts | `quantum_report.json` uses the same task/data/metric and is comparable to `baseline_report.json` |
| 3. Application Packaging | Package the result as a local/qccp-compatible showcase | <=8 attempts | Frontend/backend/API/deployment evidence is reviewable, or explicitly out of scope |
| 4. Verification & Handoff | Validate artifacts and write handoff materials without overclaiming | <=6 attempts | Report, README, INTEGRATE notes, and slides are consistent with computed artifacts |

Recommended artifacts:

```text
application_manifest.json
requirements.json
solution_plan.md
baseline_report.json
quantum_report.json
verification_report.md
README.md
INTEGRATE.md
```

Each stage saves artifacts in the user-specified or current project artifact location selected by the caller. Do not assume a default directory; record the actual paths used.

`application_manifest.json` is the application-level contract. It records `delivery_profile`, actual artifact paths, `algorithm`, `local_demo`, `qccp_web`, `docs`, verification commands, and limitations. Create it in planning and update it after each stage.

Allowed `delivery_profile` values:

- `algorithm_only`: algorithm evidence only.
- `local_fastapi_demo`: algorithm evidence plus a local FastAPI demo.
- `qccp_web_page`: algorithm evidence plus a qccp-web Vue SFC page.
- `full_delivery`: algorithm evidence, local demo, qccp-web page, and docs.

## The Stage Loop

Within every stage, repeat this cycle for each attempt:

1. **Generate**: State the hypothesis or implementation plan.
2. **Execute**: Run the smallest command that can produce evidence.
3. **Record**: Log commands, parameters, outputs, metrics, and artifact paths immediately.
4. **Diagnose**: Compare results to the gate. If results miss the gate, load `application-debugging`.
5. **Revise**: Advance only when the gate is met; otherwise plan the next attempt or stop with a clear blocker.

## Stage 1: Application Scope & Baseline

Goal: Convert the selected route into structured requirements and a runnable classical baseline.

Gate: Requirements, inputs, outputs, task type, primary metric, `higher_is_better`, dataset/split, and baseline result are explicit and reproducible.

Process:

1. Write or update `requirements.json`.
2. Write or update `application_manifest.json` with profile-specific contracts, artifact paths, validation commands, and limitations.
3. Write or update `solution_plan.md`.
4. Implement or locate the classical baseline.
5. Produce `baseline_report.json` with metric value, command, data reference, seed when relevant, and limitations.
6. Record anomalies, leakage risks, missing data, or unresolved assumptions.

## Stage 2: Quantum Method Implementation

Goal: Implement the quantum method with Cqlib and compare it against Stage 1.

Gate: `quantum_report.json` is produced from the same task/data/metric as `baseline_report.json`, records backend/shots/seed when relevant, and supports a fair comparison.

Skill routing:

- QAOA, QUBO, Ising, MaxCut, portfolio, scheduling, unit commitment -> `cqlib-sdk` + `cqlib-qaoa`
- VQE, molecular energy, Pauli Hamiltonian -> `cqlib-sdk` + `cqlib-vqe`
- VQC/QML classifier or regressor -> `cqlib-sdk` + `cqlib-qml`
- QLSTM/HQNN/hybrid neural model -> `cqlib-sdk` + `cqlib-hybrid`

Process:

1. Select the algorithm route from task type and data.
2. Keep encoding, ansatz, objective/observable, optimizer, backend execution, and result analysis separate.
3. Run local simulator or authorized backend only.
4. Produce `quantum_report.json` using the application artifact contract.
5. Update `application_manifest.json` with the actual `quantum_report.json` path and relevant quantum evidence paths.
6. Compare against `baseline_report.json`; if the method underperforms or is not comparable, diagnose before changing multiple variables.

## Stage 3: Application Packaging

Goal: Package the validated workflow into a reviewable local or qccp showcase surface.

Gate: UI, API/service contract, deployment notes, and build/test evidence are reviewable, or the caller explicitly marks packaging out of scope.

Skill routing:

- qccp visual and interaction design -> `qccp-ui`
- qccp Vue page artifacts -> `qccp-frontend`
- local FastAPI demo or qccp backend/API/deployment artifacts -> `qccp-service`

Process:

1. Read `application_manifest.json` and define the selected profile workflow.
2. For `local_fastapi_demo`, use `qccp-service` to build the FastAPI backend, local HTML demo, endpoint contract, and static asset contract.
3. For `qccp_web_page`, use `qccp-ui` and `qccp-frontend` to build Vue SFC, scoped SCSS, Element Plus, i18n, route snippet, and API paths consumed from the manifest contract.
4. Keep local FastAPI demo frontend separate from qccp-web SFC artifacts.
5. Keep simulator, cloud, and real-hardware execution assumptions explicit.
6. Update `INTEGRATE.md` with copy destinations, route, endpoint contract, profile-specific verification status, and commands.

## Stage 4: Verification & Handoff

Goal: Verify artifact consistency with `validate_quantum_application` and prepare delivery materials.

Gate: `verification_report.md`, `README.md`, `INTEGRATE.md`, and slide/showcase text are consistent with requirements, baseline report, quantum report, and app evidence.

Process:

1. Re-read `application_manifest.json`, `requirements.json`, `baseline_report.json`, `quantum_report.json`, and app evidence.
2. Cross-check metric values, commands, dataset/split, backend, API/frontend contracts, qccp route, and limitations.
3. Run `validate_quantum_application(app_dir)` on the application artifact directory.
4. Write `verification_report.md` with comparison, missing evidence, validation blockers, failures, and limitations.
5. Write or update `README.md` and `INTEGRATE.md`.
6. Prepare slide/showcase text through `showcase-slides` when needed.
7. Blockers must be fixed or reported by layer instead of hidden in final wording.

## Integrating application-debugging for Diagnosis

When a stage attempt fails, use `application-debugging`:

1. Run the 5-step diagnostic flow: observe, hypothesize, test, conclude, prescribe.
2. The diagnosis does not consume stage budget.
3. The diagnosis output becomes the plan for the next attempt.
4. Return to this pipeline and record the diagnosis in the trajectory log.

Trigger points:

- Stage 1: baseline cannot run, metric is missing, or data assumptions are unclear.
- Stage 2: quantum result is not comparable, unstable, or consistently worse than baseline.
- Stage 3: frontend/backend contract mismatch, missing build evidence, or unclear deployment boundary.
- Stage 4: README/report numbers drift, limitations are missing, or claims exceed evidence.

## Code Trajectory Logging

Every attempt should be logged:

- Attempt number and stage
- **Skill Used**: skill(s) actually used, such as `cqlib-qaoa`, `qccp-frontend`, or `delivery-writing`
- Hypothesis: what you expected and why
- Code or artifact changes
- Result: metrics, checks, observations, and paths
- Analysis: whether the hypothesis was confirmed and what changed next

See `references/code-trajectory-logging.md` for the full logging format and how logs feed into `application-memory`.

## Deterministic Validation Tool

`validate_quantum_application(app_dir, require_quantum_improvement=True, require_packaging=True)` is the deterministic delivery check.

Use it after Stage 4 artifacts exist and before final readiness claims. It checks the manifest, requirements, baseline and quantum reports, packaging evidence, documentation, and claim boundaries. It does not replace engineering review.

## Handoff to Writing and Slides

When Stage 4 passes or known blockers are documented, hand off:

| Artifact | Used by |
|----------|---------|
| `application_manifest.json` | `delivery-writing`, `delivery-review`, `showcase-slides` |
| `requirements.json` | README and verification report |
| `baseline_report.json` | comparison narrative |
| `quantum_report.json` | algorithm evidence |
| `verification_report.md` | final readiness boundary |
| `INTEGRATE.md` | qccp/local integration handoff |

## Skill Integration

| Situation | Skill |
|-----------|-------|
| Need selected route artifacts before execution | `delivery-planning` |
| Stage failure needs diagnosis | `application-debugging` |
| Quantum implementation | `cqlib-sdk` plus route-specific Cqlib skill |
| App packaging | `qccp-service`, `qccp-ui`, `qccp-frontend` |
| Completion docs/deck | `delivery-writing`, `delivery-review`, `showcase-slides` |

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Attempt budgets | `references/attempt-budget-guide.md` | When a stage is stuck |
| Trajectory logging | `references/code-trajectory-logging.md` | Every stage attempt |
| Stage protocol details | `references/stage-protocols.md` | When expanding the 4-stage plan |
| Pipeline tracker | `assets/pipeline-tracker-template.md` | Optional tracker file |
| Stage log | `assets/stage-log-template.md` | Optional per-stage log |
