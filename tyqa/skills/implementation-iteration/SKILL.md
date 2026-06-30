---
name: implementation-iteration
description: "Guides higher-effort implementation iteration for quantum application code through plan -> code -> evaluate -> refine cycles. Runs lint/tests, self-evaluation, and targeted repair for Cqlib algorithms, baselines, qccp frontend/backend artifacts, validation scripts, and delivery package code. Use when the user selects More Effort mode or application code needs quality loops. Do NOT use for single-pass Lite generation, full stage orchestration (use application-pipeline), or diagnosing a specific failed stage (use application-debugging)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, implementation, iteration, testing]
---

# Implementation Iteration

Iterate on implementation quality through plan -> code -> evaluate -> refine cycles. Use this skill when a quantum application code task deserves multiple feedback loops instead of one-pass generation.

## When to Use This Skill

- Main agent delegates a code task prefixed with `MODE: MORE_EFFORT`.
- User selected More Effort mode for code generation.
- Task spans multiple files or cross-module contracts.
- Code affects Cqlib algorithms, baseline scripts, qccp frontend/backend artifacts, validation scripts, or delivery package code.
- The task needs tests, lint checks, and structured self-evaluation before returning.

## When NOT to Use

- Single-pass code generation is enough -> use Lite mode.
- Orchestrating baseline -> quantum -> packaging -> validation -> use `application-pipeline`.
- Diagnosing why a stage failed before coding a fix -> use `application-debugging`.
- Writing prose-only handoff docs -> use `delivery-writing`.

## Before Starting

1. Read the task, relevant files, and any `application_manifest.json` or reports that define contracts.
2. Check whether `application-memory` has relevant implementation strategies.
3. Identify existing tests, linting config, and local commands.
4. Select a project-local artifact/log location if iteration notes are needed. Do not assume a fixed directory.

Check tools only when they are relevant:

```bash
ruff --version
python -m pytest --version
```

If a tool is missing, record that the check was skipped; do not fail the task solely because the tool is unavailable.

## Phase Decomposition

Break the task into sequential phases:

| Task complexity | Recommended phases |
|-----------------|--------------------|
| Single file, clear behavior | 1 phase |
| 2-4 files, clear interfaces | 2 phases |
| 5+ files or cross-layer contracts | 3-5 phases |

For each phase, define:

- name
- goal
- affected files
- verification signal
- risk if wrong

## Iteration Loop

For each phase, iterate up to 3 times. Global maximum is 10 iterations unless the caller sets a smaller budget.

### Step 1: Plan

Read current code and previous feedback. Write a focused plan for this iteration.

If this is not the first iteration, diagnose why the previous attempt failed before editing again.

### Step 2: Code

Implement the plan with small, reviewable edits.

- Keep public API contracts stable unless the task requires a change.
- Preserve quantum semantics: gate order, wire order, measurement order, parameter binding, backend assumptions, and result schema.
- Avoid adding heavy dependencies unless the task explicitly requires them.
- Keep qccp/local demo contracts aligned with `application_manifest.json`.

### Step 3: Evaluate

Run the fastest relevant checks. Prefer targeted tests first.

Common checks:

```bash
ruff check <changed paths>
ruff format --check <changed paths>
python -m pytest <targeted tests>
```

For quantum code, add or run checks for:

- circuit construction
- parameter binding
- measurement/result schema
- baseline-vs-quantum comparability
- validator contract

For qccp/local app code, add or run checks for:

- request/response schema
- route/path consistency
- build/import smoke test
- static asset or component existence

### Step 4: Score

Record a compact score:

| Signal | Score input |
|--------|-------------|
| Lint/format | pass/fail/skipped |
| Tests | pass/fail/skipped and target |
| Contract check | manifest/report/API/schema status |
| Self-review | correctness, completeness, readability, error handling |

Only claim the iteration is complete when objective checks pass or skipped checks are justified.

### Step 5: Decide

- If the phase meets its verification signal, advance.
- If a specific failure remains, run another iteration.
- If the root cause is unclear, hand off to `application-debugging`.
- If the selected route or contract is wrong, hand off to `delivery-planning` or `application-intake`.

### Step 6: Log

If the task is more than a small fix, write an iteration note in the selected project artifact location:

```markdown
## Iteration N - [phase]
- Skill Used: implementation-iteration
- Changes: [...]
- Checks: [...]
- Result: [...]
- Next: [...]
```

## Failure Response Guide

| Last failure | Planned response |
|--------------|------------------|
| Syntax/import error | simplify import path, run a minimal import check |
| Test failure | focus on the failing assertion and contract |
| Timeout | reduce fixture size or add smoke mode |
| Metric mismatch | check data split, metric direction, and report schema |
| Quantum semantic issue | check qubit order, parameter binding, measurement mapping |
| qccp mismatch | check API prefix, request/response schema, route/component path |
| Validator blocker | inspect manifest paths and selected `delivery_profile` |

## Completion

Report:

- phases completed
- files changed
- checks run and results
- remaining limitations
- next handoff skill if work remains

## Handoff

| Outcome | Next skill | Payload |
|---------|------------|---------|
| Code passes targeted checks | caller or `application-pipeline` | files, checks, remaining risk |
| Stage failure persists | `application-debugging` | failing command, logs, artifact paths |
| Contract needs redesign | `delivery-planning` | mismatch and proposed contract change |
| Docs need update | `delivery-writing` | changed behavior and verified commands |
| Reusable implementation lesson | `application-memory` | pattern, evidence, applicability |

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Scoring rules and edge cases | `references/evaluation-protocol.md` | When pass/fail evidence is mixed |
| Iteration log template | `assets/iteration-log-template.md` | For longer multi-iteration tasks |
