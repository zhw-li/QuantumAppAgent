---
name: application-debugging
description: "Guides structured diagnosis and repair for failed quantum application stages: baseline errors, non-comparable quantum reports, Cqlib execution failures, unstable training, metric drift, qccp API/UI mismatches, packaging gaps, and validation blockers. Use when a run, artifact, algorithm, data path, frontend/backend integration, or delivery check does not work. Do NOT use for initial route design (use application-intake), broad stage orchestration (use application-pipeline), or final docs (use delivery-writing)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, debugging, diagnosis]
---

# Application Debugging

Diagnose why a quantum application stage failed and prescribe the smallest repair that can be verified. The target is not "try more"; it is isolate the cause, fix one factor, and return to `application-pipeline`.

## When to Use This Skill

- Baseline code does not run or produces an unusable `baseline_report.json`.
- `quantum_report.json` is missing, unstable, or not comparable to the baseline.
- Cqlib circuit construction, parameter binding, backend execution, or result parsing fails.
- Training does not converge or metrics drift across seeds.
- qccp API/UI integration breaks, endpoint schemas disagree, or build evidence is missing.
- `validate_quantum_application(app_dir)` reports blockers.
- User asks why a quantum application stage does not work.

## When NOT to Use

- Designing a new route -> use `application-intake`.
- Planning stage gates before execution -> use `delivery-planning`.
- Running the whole delivery pipeline -> use `application-pipeline`.
- Fixing an isolated syntax/import error with no stage diagnosis needed -> use the code/debug agent directly.
- Capturing reusable lessons after completion -> use `application-memory`.

## 5-Step Diagnostic Flow

### Step 1: Observe the Failure

Collect concrete evidence:

- command run and exit code
- stack trace or validation error
- input data/sample
- expected vs actual schema
- metric value and direction
- artifact path and missing fields
- simulator/cloud/hardware assumptions

Do not diagnose from a summary alone when logs or artifacts are available.

### Step 2: Find a Working Reference

Create the simplest passing reference:

- smaller dataset or synthetic known case
- classical baseline only
- statevector/simulator before shots or hardware
- one route layer at a time: algorithm, API, UI, docs
- previous successful artifact from `application-memory` when available

If no reference works, simplify until one does.

### Step 3: Bridge the Gap

Add back one factor at a time:

- data complexity
- encoding
- ansatz/model depth
- optimizer/settings
- backend/shots/noise
- API serialization
- qccp route/style/i18n
- validator-required artifact fields

The cause should be atomic enough that a single next edit can test it.

### Step 4: Hypothesize and Verify

List possible causes, rank them, and run targeted checks:

| Failure type | Likely checks |
|--------------|---------------|
| Baseline mismatch | data split, metric direction, output schema |
| Quantum underperformance | encoding, ansatz expressivity, objective, optimizer, seeds |
| Circuit/runtime error | qubit order, unsupported gate, parameter binding, backend options |
| Report mismatch | missing fields, stale paths, different dataset/metric |
| API/UI mismatch | request schema, response schema, route prefix, static assets |
| Validator blocker | manifest path, delivery_profile layer, docs consistency |

Confirm the cause with evidence before editing multiple variables.

### Step 5: Prescribe and Verify the Fix

For the selected fix:

1. State the minimal change.
2. Explain why it targets the confirmed cause.
3. Run the smallest command or validator check that proves it worked.
4. Record remaining risk.
5. Return to `application-pipeline` with the next stage action.

## Logging

Use `assets/experiment-log-template.md` as a generic diagnostic log if the project has no existing log template. Record:

- purpose
- setting
- result
- analysis
- next step

When used from `application-pipeline`, include the pipeline stage and **Skill Used** in the trajectory log.

## Handoff

| Outcome | Next skill | Payload |
|---------|------------|---------|
| Cause fixed | `application-pipeline` | command, artifact paths, verification result |
| Needs code quality loop | `implementation-iteration` | failing checks and target files |
| Needs route change | `application-intake` or `delivery-planning` | confirmed blocker and rejected assumptions |
| Needs reusable memory | `application-memory` | failure pattern, fix, applicability |
| Needs docs update | `delivery-writing` | corrected evidence and limitations |

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Diagnostic methodology | `references/debugging-methodology.md` | Complex or repeated failures |
| Log template | `assets/experiment-log-template.md` | Recording stage diagnosis |
