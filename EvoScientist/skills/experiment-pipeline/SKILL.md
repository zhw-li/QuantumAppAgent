---
name: experiment-pipeline
description: "Guides structured 4-stage quantum application execution with attempt budgets and stage gate conditions: Stage 1 application scope and classical baseline, Stage 2 cqlib quantum method implementation, Stage 3 qccp application packaging, Stage 4 verification and handoff. Integrates with evo-memory, experiment-craft, cqlib skills, qccp skills, paper-writing, and academic-slides. Use when: user has a planned quantum application, needs to organize baseline-first validation, package a cloud showcase, or decide when to advance to the next delivery stage. Do NOT use for open-ended literature search (use paper-navigator/research-survey), idea generation (use research-ideation), standalone qccp implementation (use qccp-frontend/qccp-service), or final prose polishing only (use paper-writing)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [core, experimentation, experiment-design, quantum-application]
---

# Experiment Pipeline

A structured 4-stage framework for delivering quantum applications from requirements and baseline through quantum implementation, app packaging, and verification handoff. This keeps the native EvoScientist pipeline style: each stage has a goal, attempt budget, gate condition, artifact trail, and diagnosis path.

## When to Use This Skill

- User has a planned quantum application or PoC and needs to organize execution.
- User wants baseline-first validation before making quantum claims.
- User needs a cqlib algorithm, qccp page/API packaging, or cloud showcase readiness.
- User asks about experiment stages, attempt budgets, stage gates, or when to move on.
- User needs reproducible artifacts for README, INTEGRATE, verification report, or slides.

## When NOT to Use

- **Open-ended paper discovery or survey** -> use `paper-navigator` or `research-survey`.
- **Finding candidate application directions** -> use `research-ideation`.
- **Planning only, before implementation begins** -> use `paper-planning`.
- **Standalone frontend/backend artifact generation** -> use `qccp-ui`, `qccp-frontend`, or `qccp-service`.
- **Prose-only delivery writing or slides** -> use `paper-writing` or `academic-slides`.

## Pipeline Mindset

Quantum applications fail for two reasons: unverifiable comparison and unreviewable packaging. A simulator result without a baseline is not evidence, and an algorithm without an API/page/handoff cannot be showcased. The pipeline enforces order, limits unproductive retries, and keeps claims tied to artifacts.

Do not run TianYan/GuoDun hardware jobs unless the user explicitly authorizes the run and provides credentials through environment variables or ignored local config. Simulator results must not be described as real-hardware performance.

## Before Starting: Load Prior Knowledge

If coming from `research-ideation` or `paper-planning`, use the proposal to define task type, dataset, baseline, primary metric, and expected artifacts.

Before entering the pipeline, load Experimentation Memory (M_E) from prior cycles when available:

1. Refer to the **evo-memory** skill.
2. Select the top-1 entry most relevant to the current quantum application domain.
3. Use the selected strategy to inform baseline design, quantum encoding/ansatz choices, debugging, and packaging.
4. If no relevant memory exists, skip this step and proceed.

## 4-Stage Pipeline Overview

Each stage follows a **generate -> execute -> record -> diagnose -> revise** loop:

| Stage | Goal | Budget | Gate Condition |
|-------|------|--------|----------------|
| 1. Application Scope & Baseline | Structure requirements and produce a runnable classical baseline | <=10 attempts | Requirements, data, primary metric, and baseline result are explicit and reproducible |
| 2. Quantum Method Implementation | Implement the cqlib quantum method and compare against the baseline | <=12 attempts | `quantum_report.json` uses the same task/data/metric and is comparable to `baseline_report.json` |
| 3. Application Packaging | Package the result as a qccp-compatible UI/API/deployment showcase | <=8 attempts | Frontend/backend/API/deployment evidence is reviewable, or explicitly out of scope |
| 4. Verification & Handoff | Write verification and delivery materials without overclaiming | <=6 attempts | Report, README, INTEGRATE notes, and slides are consistent with computed artifacts |

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

### The Stage Loop

Within every stage, repeat this cycle for each attempt:

1. **Generate**: State the hypothesis or implementation plan for this attempt.
2. **Execute**: Run the smallest command that can produce evidence.
3. **Record**: Log commands, parameters, outputs, metrics, and artifact paths immediately.
4. **Diagnose**: Compare results to the stage gate condition. If results do not match expectations, load `experiment-craft`.
5. **Revise**: Advance only when the gate condition is met; otherwise plan the next attempt or stop with a clear blocker.

## Stage 1: Application Scope & Baseline

**Goal**: Convert the user request into structured requirements and a runnable classical baseline.

**Why this matters**: Without a clear task, dataset, primary metric, and baseline, the quantum result cannot be interpreted.

**Budget**: <=10 attempts.

**Gate**: Requirements, inputs, outputs, task type, primary metric, metric direction, dataset/split, and baseline result are explicit and reproducible.

**Process**:

1. Write or update `requirements.json`.
2. Write or update `application_manifest.json` with `delivery_profile`, task, primary metric, artifact paths, profile-specific contracts, verification commands, and limitations.
3. Write `solution_plan.md` with stages, success signals, commands, and expected artifacts.
4. Implement or locate the classical baseline.
5. Produce `baseline_report.json` with metric value, command, data reference, seed when relevant, and limitations.
6. Record anomalies, leakage risks, missing data, or unresolved assumptions.

**Output**: Requirements, baseline code/results, and baseline report saved in the selected artifact location.

## Stage 2: Quantum Method Implementation

**Goal**: Implement the quantum method with cqlib and compare it against the Stage 1 baseline.

**Why this matters**: Quantum claims require comparable data, metric direction, and execution settings.

**Budget**: <=12 attempts.

**Gate**: `quantum_report.json` is produced from the same task/data/metric as `baseline_report.json`, records backend/shots/seed when relevant, and supports a fair comparison.

**Skill routing**:

- QAOA, QUBO, Ising, MaxCut, portfolio, scheduling, unit commitment -> `cqlib-sdk` + `cqlib-qaoa`
- VQE, molecular energy, Pauli Hamiltonian -> `cqlib-sdk` + `cqlib-vqe`
- VQC/QML classifier or regressor -> `cqlib-sdk` + `cqlib-qml`
- QLSTM/HQNN/hybrid neural model -> `cqlib-sdk` + `cqlib-hybrid`

**Process**:

1. Select the algorithm route from task type and data.
2. Keep encoding, ansatz, objective/observable, optimizer, backend execution, and result analysis separate.
3. Run local simulator or authorized backend only.
4. Produce `quantum_report.json` using the cqlib artifact contract.
5. Update `application_manifest.json` with the actual `quantum_report.json` path and relevant quantum evidence paths.
6. Compare against `baseline_report.json`; if the method underperforms or is not comparable, diagnose before changing multiple variables.

**Output**: Quantum code, command logs, raw results, and `quantum_report.json` saved in the selected artifact location.

## Stage 3: Application Packaging

**Goal**: Package the validated workflow into a reviewable cloud showcase surface.

**Why this matters**: A quantum application must be demonstrable through a user workflow, not only an algorithm script.

**Budget**: <=8 attempts.

**Gate**: UI, API/service contract, deployment notes, and build/test evidence are reviewable, or the caller explicitly marks packaging out of scope.

**Skill routing**:

- qccp visual and interaction design -> `qccp-ui`
- qccp Vue page artifacts -> `qccp-frontend`
- qccp backend/API/deployment artifacts -> `qccp-service`

**Process**:

1. Read `application_manifest.json` and define the selected profile workflow.
2. For `local_fastapi_demo`, use `qccp-service` to build the FastAPI backend, local HTML demo, endpoint contract, and static asset contract.
3. For `qccp_web_page`, use `qccp-ui` and `qccp-frontend` to build Vue SFC, scoped SCSS, Element Plus, i18n, route snippet, and API paths consumed from the manifest contract.
4. Keep local FastAPI demo frontend separate from qccp-web SFC artifacts.
5. Keep simulator, cloud, and real-hardware execution assumptions explicit.
6. Update `INTEGRATE.md` with copy destinations, route, endpoint contract, profile-specific verification status, and commands.

**Output**: Frontend/backend/deployment evidence saved in the selected artifact location or the caller-provided qccp output location.

## Stage 4: Verification & Handoff

**Goal**: Verify artifact consistency with `validate_quantum_application` and prepare delivery materials.

**Why this matters**: Delivery language must match computed artifacts. Simulator evidence cannot become real-hardware claims.

**Budget**: <=6 attempts.

**Gate**: `verification_report.md`, `README.md`, `INTEGRATE.md`, and slide/showcase text are consistent with requirements, baseline report, quantum report, and app evidence.

**Process**:

1. Re-read `application_manifest.json`, `requirements.json`, `baseline_report.json`, `quantum_report.json`, and app evidence.
2. Cross-check metric values, commands, dataset/split, backend, API/frontend contracts, qccp route, and limitations.
3. Run `validate_quantum_application(app_dir)` on the application artifact directory.
4. Write `verification_report.md` with comparison, missing evidence, validation blockers, failures, and limitations.
5. Write or update `README.md` and `INTEGRATE.md`.
6. Prepare slide/showcase text through `academic-slides` when needed.
7. Mark unresolved evidence as blockers instead of writing customer-facing readiness claims.

**Output**: Verification report, docs, and presentation notes saved in the selected artifact location.

## Integrating experiment-craft for Diagnosis

When a stage attempt fails, refer to the **experiment-craft** skill for structured diagnosis:

1. Follow the experiment-craft diagnostic protocol.
2. Run the 5-step diagnostic flow: observe, hypothesize, test, conclude, prescribe.
3. The diagnosis does not consume your stage budget.
4. The diagnosis output becomes the plan for the next attempt.
5. Return to this pipeline and record the diagnosis in the trajectory log.

Trigger points:

- Stage 1: baseline cannot run, metric is missing, or data assumptions are unclear.
- Stage 2: quantum result is not comparable, unstable, or consistently worse than baseline.
- Stage 3: frontend/backend contract mismatch, missing build evidence, or unclear deployment boundary.
- Stage 4: README/report numbers drift, limitations are missing, or claims exceed evidence.

## Code Trajectory Logging

Every attempt across all stages should be logged in a structured format:

- **Attempt number** and stage
- **Skill Used**: skill(s) actually used for the attempt, such as `cqlib-qaoa`, `qccp-frontend`, or `paper-writing`
- **Hypothesis**: what you expected and why
- **Code or artifact changes**: summary of what changed
- **Result**: metrics, checks, observations, and paths
- **Analysis**: whether the hypothesis was confirmed and what changed next

See [references/code-trajectory-logging.md](references/code-trajectory-logging.md) for the full logging format and how logs feed into `evo-memory`.

## Counterintuitive Pipeline Rules

1. **Baseline is part of the application**: It defines what the quantum method must be compared against.
2. **Comparability beats optimism**: Same data, metric, direction, and task definition matter more than a better-looking number.
3. **Packaging is evidence**: A cloud showcase needs route/API/deployment proof, not only screenshots or prose.
4. **Verification can block handoff**: Missing artifacts, validator blockers, or overclaimed hardware behavior should stop delivery language.
5. **Failed attempts are data**: Log failures carefully so `evo-memory` can improve future cycles.
6. **Early termination is a feature**: Stop when the stage gate is clearly unreachable under current assumptions.

## Deterministic Validation Tool

Before final handoff, call `validate_quantum_application(app_dir)` on the artifact directory. The tool reads `delivery_profile` and runs only that profile's layers: `algorithm`, `local_demo`, `qccp_web`, and `docs`. Blockers must be fixed or reported by layer.

The v1 report schema follows the `cqlib-sdk` contract:

- `task`
- `data`
- `primary_metric`
- `higher_is_better`
- `value`
- `command`
- `artifact_paths`
- optional `seed`, `backend`, `shots`, `qubits`, `circuit_depth`, and `limitations`

If the user only asks for a feasibility demo, set `require_quantum_improvement` or `require_packaging` to `false` in `requirements.json`; otherwise unresolved tool blockers must remain visible in `verification_report.md`.

## Handoff to Writing and Slides

When all four stages are complete, pass these artifacts to `paper-writing`, `paper-review`, and `academic-slides`:

| Artifact | Source Stage | Used By |
|----------|-------------|---------|
| Requirements and solution plan | Stage 1 | Summary, scope, limitations |
| Classical baseline report | Stage 1 | Comparison table |
| Quantum method report | Stage 2 | Main result and backend notes |
| App packaging evidence | Stage 3 | README, INTEGRATE, showcase |
| Verification report | Stage 4 | Limitations and delivery decision |
| Trajectory logs | All stages | Reproducibility and future memory |

Also pass results to `evo-memory` for evolution updates:

- If baseline or implementation cannot become executable within budget, trigger IVE.
- If the quantum direction underperforms after systematic attempts, trigger IVE.
- If the pipeline succeeds, trigger ESE with trajectory logs and reusable delivery lessons.

## Skill Integration

### Before Starting

Refer to **evo-memory** for relevant experimentation memory when available.

### On Failure

Refer to **experiment-craft** for diagnosis, then return to this pipeline.

### On Quantum Implementation

Refer to **cqlib-sdk** and the relevant algorithm skill.

### On App Packaging

Refer to **qccp-ui**, **qccp-frontend**, and **qccp-service**.

### On Pipeline Completion

Refer to **paper-writing**, **paper-review**, **academic-slides**, and **evo-memory**.

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Per-stage checklists and patterns | [stage-protocols.md](references/stage-protocols.md) | Detailed guidance for stage execution |
| Budget rationale and adjustment | [attempt-budget-guide.md](references/attempt-budget-guide.md) | When budgets feel too tight or too loose |
| Code trajectory logging format | [code-trajectory-logging.md](references/code-trajectory-logging.md) | Recording attempts for evo-memory |
| Stage log template | [stage-log-template.md](assets/stage-log-template.md) | Logging a single stage's progress |
| Pipeline tracker template | [pipeline-tracker-template.md](assets/pipeline-tracker-template.md) | Tracking the full 4-stage pipeline |
