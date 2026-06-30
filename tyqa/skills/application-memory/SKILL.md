---
name: application-memory
description: "Guides persistent memory for quantum application development cycles: reusable application directions, failed routes, baseline choices, Cqlib algorithm lessons, qccp integration constraints, validation blockers, tuning strategies, and cloud/hardware delivery patterns. Use when updating memory after application-intake, application-pipeline, debugging, or delivery review, or when starting a new quantum application that may benefit from prior evidence. Do NOT use for running stages (use application-pipeline), diagnosing active failures (use application-debugging), or generating routes (use application-intake)."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, memory, reuse]
---

# Application Memory

Maintain reusable knowledge across quantum application cycles. Store patterns that will change future route selection, implementation, validation, or delivery; do not store raw logs that belong in the project artifacts.

## When to Use This Skill

- `application-intake` produced route choices worth remembering.
- `application-pipeline` succeeded or failed in a way that should influence future PoCs.
- `application-debugging` found a reusable failure pattern or fix.
- `delivery-review` identified a recurring claim, packaging, or validation issue.
- User starts a new application and asks what worked before.

## When NOT to Use

- Running the pipeline or executing code -> use `application-pipeline`.
- Diagnosing an active broken run -> use `application-debugging`.
- Generating candidate routes -> use `application-intake`.
- Writing final docs -> use `delivery-writing`.

## Memory Stores

Use the project's configured memory location when available. If no project convention exists, keep memory under a clearly named, ignored project memory directory and record the path used.

### Application Direction Memory (M_A)

Stores route-level lessons:

| Section | What to store |
|---------|---------------|
| Feasible routes | application domains and algorithm families that were validated enough to retry |
| Failed routes | routes that failed, with implementation vs fundamental cause |
| Baseline lessons | fair comparators, datasets, metrics, and leakage risks |
| Delivery lessons | profiles, qccp constraints, API/UI patterns, docs requirements |

Each entry should include: summary, context, evidence artifact paths, applicability, failure classification when relevant, date, and retrieval tags.

### Implementation Strategy Memory (M_I)

Stores technical patterns:

| Section | What to store |
|---------|---------------|
| Data strategies | preprocessing, split policy, feature scaling, synthetic data construction |
| Quantum strategies | encoding, ansatz, observable/objective, optimizer, backend settings |
| Cqlib strategies | API patterns, result schema, simulator choices, parameter handling |
| Debugging strategies | checks that isolate failures quickly |
| qccp strategies | service/page contracts, route conventions, static assets, integration gotchas |

Each entry should be reusable beyond one project. Keep the evidence path so future agents can verify the origin.

## Update Triggers

### After Application Intake

Record only durable route-selection knowledge:

- promising application route and why
- rejected route and blocker
- evidence source that changed the decision
- data/baseline availability
- delivery profile feasibility

### After Pipeline Completion

Record:

- selected route and final readiness verdict
- baseline and quantum comparability lessons
- Cqlib implementation choices that mattered
- qccp/local packaging constraints
- validator blockers fixed or left open
- commands or settings that are broadly reusable

### After Debugging

Record a failure pattern only if it is likely to recur:

- symptom
- confirmed cause
- minimal fix
- verification command
- affected route/profile
- when not to apply the fix

### After Delivery Review

Record recurring review risks:

- unsupported claim patterns
- manifest/report drift
- simulator-vs-hardware wording pitfalls
- qccp integration omissions
- README/INTEGRATE gaps

## Retrieval at Cycle Start

When `application-intake`, `delivery-planning`, or `application-pipeline` starts:

1. Read the memory index or relevant memory files.
2. Select the top 1-2 entries that match the current task, data, route, or delivery profile.
3. Inject the selected lessons as assumptions or warnings.
4. Do not blindly apply old strategies; check context and evidence.

## Entry Template

```markdown
## [YYYY-MM-DD] [Short title]

- Type: feasible-route | failed-route | baseline | quantum-strategy | debugging | qccp | delivery-review
- Context: [application domain, task type, data, delivery_profile]
- Summary: [one sentence]
- Evidence: [artifact paths or commands]
- Reuse rule: [when to apply]
- Avoid rule: [when not to apply]
- Tags: [retrieval tags]
```

## Quality Rules

1. Store patterns, not transcripts.
2. Store failed routes with cause classification; failed implementation is not the same as failed idea.
3. Keep artifact paths so claims can be audited.
4. Prune stale entries when they stop influencing decisions.
5. Never store secrets, credentials, private endpoints, or account-specific cloud details.

## Handoff

| Source skill | What to store |
|--------------|---------------|
| `application-intake` | route ranking, selected/rejected routes, evidence gaps |
| `delivery-planning` | manifest/profile/validation planning choices |
| `application-pipeline` | stage outcomes, reports, validator findings |
| `application-debugging` | confirmed cause and reusable fix |
| `delivery-review` | package review risks and claim boundaries |

## Reference Navigation

Existing memory protocol references can be used as implementation detail, but adapt them to application delivery:

| Topic | Reference File | Use |
|-------|---------------|-----|
| Direction update protocol | `references/ide-protocol.md` | Route selection memory |
| Failure classification | `references/ive-protocol.md` | Failed route classification |
| Strategy extraction | `references/ese-protocol.md` | Reusable implementation strategy |
| Memory schema | `references/memory-schema.md` | Field consistency |
