---
name: application-intake
description: "Conversational intake for end-to-end quantum algorithm application development: clarify user goals, inputs/outputs, task type, data status, baseline, primary metric, quantum route, Cqlib/qccp delivery target, hardware authorization, and validation plan; generate and rank Top-3 feasible application routes; produce application_brief.md, requirements.json draft, application_manifest.json draft, solution_plan.md draft, algorithm_route.md, and validation_plan.md. Use when the user wants to shape a quantum application, PoC, Cqlib demo, cloud showcase, or algorithm route before implementation. Do NOT use for deep evidence discovery (use evidence-navigator), broad solution maps (use solution-landscape), detailed stage planning (use delivery-planning), or staged execution (use application-pipeline)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, intake, requirements, routing]
---

# Application Intake

Guide the user from an open-ended quantum application request to a ranked, implementable application route. This is the conversational front door for the full lifecycle; it does not replace detailed implementation or validation.

```
Step 0: Load application-memory
    ->
Step 1: Conversational requirement intake
    ->
Step 2: Application framing
    ->
Step 3: Evidence grounding (conditional)
    ->
Step 4: Generate candidate routes
    ->
Step 5: Rank Top-3 routes
    ->
Step 6: User selects or combines routes
    ->
Step 7: Produce handoff artifacts
    ->
Step 8: Hand off to delivery-planning or application-pipeline
```

## When to Use

- User wants to turn a business, engineering, or scientific problem into a quantum algorithm application.
- User needs dialogue-style clarification before coding: task type, input/output, data, baseline, metric, route, delivery profile, constraints, or hardware boundary.
- User wants multiple candidate application scenarios or Cqlib/qccp showcase routes and a recommendation.
- User has a vague PoC idea and needs a concrete `application_manifest.json` and validation plan draft.
- User asks whether a quantum approach is worth trying, but does not yet need full implementation.

## When NOT to Use

- Finding, reading, or evaluating papers/repos/datasets in depth -> use `evidence-navigator`.
- Creating a broad method/baseline/platform map -> use `solution-landscape`.
- Converting a selected route into stage gates and artifact contracts -> use `delivery-planning`.
- Executing baseline, quantum code, packaging, and validation -> use `application-pipeline`.
- Debugging a failed run or broken API/UI -> use `application-debugging`.

## Step 0: Load Prior Knowledge

Before proposing routes, use `application-memory` when prior cycles may matter.

1. Look for reusable application directions, failed routes, Cqlib implementation lessons, qccp constraints, and hardware/cloud limitations.
2. Bring in only the top 1-2 relevant entries. Do not overload the intake with stale memory.
3. Treat previous failures as evidence, not absolute bans. Reopen a failed route only when the current task changes the blocker.

## Step 1: Conversational Requirement Intake

Ask concise questions until these fields are clear enough to draft artifacts. If the user already provided an answer, do not ask again.

| Field | What to capture |
|-------|-----------------|
| Application goal | Who uses it, what decision/action it supports, and what "done" means |
| Inputs and outputs | Input schema, output schema, expected units/classes/ranking, and error cases |
| Task type | Optimization, classification, regression, simulation, search, chemistry, finance, scheduling, QML, or hybrid workflow |
| Data status | Provided dataset, public dataset, synthetic data, private data, missing data, split policy, leakage risks |
| Baseline | Classical solver/model/rule, current manual process, paper baseline, or acceptable fallback |
| Primary metric | Metric name, direction (`higher_is_better`), minimum useful threshold, runtime or cost limits |
| Quantum route | Candidate algorithm family: QAOA/QUBO, VQE, VQC/QML, hybrid model, amplitude/phase estimation, simulator-only demo |
| Delivery target | `algorithm_only`, `local_fastapi_demo`, `qccp_web_page`, or `full_delivery` |
| Hardware boundary | Simulator, cloud backend, real hardware authorization, credentials via env/config, shot limits, quota/cost constraints |
| Evidence standard | Internal PoC, customer demo, benchmark, reproducibility package, or publication-grade novelty |

If information is missing but not blocking, state the assumption in the draft artifacts and continue.

## Step 2: Application Framing

Convert the intake into a crisp problem statement:

- **User workflow**: What the user uploads/selects, what the system computes, and what the user sees.
- **Algorithm contract**: Data in, circuit/model route, backend assumptions, metric out.
- **Comparison contract**: Baseline and quantum method must use the same data, split, metric, and direction.
- **Delivery contract**: Which `delivery_profile` layers are in scope and which are explicitly out of scope.
- **Risk register**: Missing data, weak baseline, non-comparable metrics, simulator-only evidence, cloud/hardware authorization, UI/API integration risks.

## Step 3: Evidence Grounding

Use evidence only to the depth required by the project:

- **Ordinary PoC**: Do a lightweight check for baseline methods, public datasets, comparable metrics, and known algorithm fit. Use `evidence-navigator` only when local knowledge is insufficient or the user asks for sources.
- **Customer or benchmark delivery**: Use `evidence-navigator` to verify baseline choices, datasets, comparable implementations, and platform constraints.
- **Publication-grade novelty**: Use `evidence-navigator` for deep paper collection and, when useful, `solution-landscape` for a structured method map before route ranking.

Do not block an engineering PoC on 30-50 papers unless novelty or defensible external evidence is a requirement.

## Step 4: Generate Candidate Routes

Produce 3-5 candidate application routes. Each route should be implementable, comparable, and deliverable.

Route format:

```markdown
## Route: [short name]
- Problem fit: [why this route matches the task]
- Quantum method: [algorithm family, encoding, ansatz/objective/observable, backend]
- Baseline: [classical comparator and why it is fair]
- Data path: [provided/public/synthetic data and split]
- Delivery profile: [algorithm_only/local_fastapi_demo/qccp_web_page/full_delivery]
- Expected artifacts: [requirements, manifest, reports, UI/API/docs]
- Main risk: [single biggest blocker]
- Validation signal: [metric, command, or artifact check]
```

Use the Cqlib skill routing:

| Task pattern | Preferred skill route |
|--------------|-----------------------|
| QUBO, MaxCut, scheduling, portfolio, combinatorial optimization | `cqlib-sdk` + `cqlib-qaoa` |
| Molecular energy, Hamiltonian expectation, chemistry demo | `cqlib-sdk` + `cqlib-vqe` |
| Classification/regression with quantum feature maps or VQC | `cqlib-sdk` + `cqlib-qml` |
| QLSTM, HQNN, hybrid neural workflow | `cqlib-sdk` + `cqlib-hybrid` |
| qccp API or local FastAPI demo | `qccp-service` |
| qccp-web page | `qccp-ui` + `qccp-frontend` |

## Step 5: Rank Top-3 Routes

Rank candidates with a compact scorecard. Prefer routes that can be validated with concrete artifacts over routes that sound more novel but cannot be compared.

| Dimension | Meaning |
|-----------|---------|
| Application value | Solves the user's actual workflow or decision |
| Feasibility | Data, baseline, Cqlib implementation, and runtime are realistic |
| Quantum fit | The quantum route is structurally justified, not decorative |
| Comparability | Baseline and quantum metrics can be fairly compared |
| Delivery readiness | The selected profile can be packaged and verified |
| Risk | Lower score for hidden data, cloud, hardware, or integration blockers |

Present:

```markdown
## Top-3 Quantum Application Routes

| Rank | Route | Method | Baseline | Metric | Delivery profile | Main risk | Score |
|------|-------|--------|----------|--------|------------------|-----------|-------|
| 1 | ... | ... | ... | ... | ... | ... | ... |
| 2 | ... | ... | ... | ... | ... | ... | ... |
| 3 | ... | ... | ... | ... | ... | ... | ... |
```

Then include the full route card for each Top-3 candidate. Ask the user to select one route, combine routes, or approve the recommended route.

## Step 6: Produce Handoff Artifacts

After the user selects a route, draft the handoff files in the selected project/artifact location. Do not assume a fixed directory; state the path used.

Required drafts:

- `application_brief.md`: user goal, workflow, inputs/outputs, assumptions, and out-of-scope items.
- `requirements.json`: structured requirements, data, metric, baseline, backend, and delivery profile.
- `application_manifest.json`: draft application contract with `delivery_profile`, artifact paths, algorithm, local demo, qccp web, docs, validation commands, and limitations.
- `solution_plan.md`: staged plan and success signals.
- `algorithm_route.md`: encoding, ansatz/objective/observable, optimizer/backend, and result schema.
- `validation_plan.md`: baseline/quantum comparability, primary metric, commands, `validate_quantum_application(app_dir)`, and blockers.

## Step 7: Handoff

| Next step | Target skill | Handoff payload |
|-----------|--------------|-----------------|
| Need deeper evidence before selection | `evidence-navigator` or `solution-landscape` | Search queries, baseline/dataset questions, route hypotheses |
| Route selected but stage plan not detailed | `delivery-planning` | Top route, draft artifacts, risks, delivery profile |
| Ready to implement | `application-pipeline` | `requirements.json`, `application_manifest.json`, `solution_plan.md`, `algorithm_route.md`, `validation_plan.md` |
| Need algorithm implementation | `cqlib-*` skills | Task type, data contract, metric, route card |
| Need qccp packaging | `qccp-*` skills | Manifest, API/UI contract, selected delivery profile |
| Need docs or deck | `delivery-writing`, `delivery-review`, `showcase-slides` | Verified artifacts and claims boundary |

## Output Quality Rules

1. Do not overpromise quantum advantage. Write "candidate quantum route" until evidence exists.
2. Do not silently change the metric direction. Record `higher_is_better` or equivalent explicitly.
3. Do not treat simulator output as hardware evidence.
4. Do not ask for secrets in chat. Use environment variables or ignored local config.
5. Keep route cards small enough that the user can choose between them.
6. Prefer a narrow, verifiable PoC over a broad demo that cannot be validated.

## References & Assets

Existing reference files in this skill can still support ranking and route selection:

| Resource | Use |
|----------|-----|
| `references/elo-ranking-guide.md` | Optional pairwise ranking rubric |
| `references/problem-selection.md` | Risk and feasibility checks |
| `references/solution-design.md` | Route construction heuristics |
| `references/tree-search-protocol.md` | Wider search when many route families are viable |
| `assets/ranking-scorecard-template.md` | Optional route scorecard template |
