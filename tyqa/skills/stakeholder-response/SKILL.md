---
name: stakeholder-response
description: "Guides responses to customer, reviewer, manager, or internal objections about a quantum application delivery: baseline fairness, weak metrics, simulator-vs-hardware limits, qccp integration gaps, validation failures, timeline, unsupported claims, and requested scope changes. Use when feedback or objections arrive after review/demo. Do NOT use for first-pass writing (use delivery-writing), self-review (use delivery-review), or executing fixes (use application-pipeline)."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, stakeholder-response, feedback]
---

# Stakeholder Response

Answer external or internal concerns with evidence, boundaries, and a concrete next action. The response should protect credibility: acknowledge real gaps, correct misunderstandings, and avoid unsupported promises.

## When to Use This Skill

- Customer asks whether the result proves quantum advantage.
- Reviewer questions the baseline, metric, data split, or validation method.
- Manager asks why a qccp/cloud demo is not ready.
- Internal team flags simulator-only evidence or hardware authorization gaps.
- User needs a concise written response to feedback after a PoC demo or package review.

## When NOT to Use

- Writing README/INTEGRATE/verification docs from scratch -> use `delivery-writing`.
- Reviewing the package before feedback -> use `delivery-review`.
- Fixing the underlying code/artifacts -> use `application-pipeline`.
- Diagnosing a failed command -> use `application-debugging`.

## Response Workflow

### Step 1: Classify the Concern

| Concern type | Examples |
|--------------|----------|
| Evidence gap | missing baseline, weak metric, no uncertainty, missing validator output |
| Comparability | different data split, metric direction mismatch, unfair baseline |
| Hardware/cloud | simulator-only result, no authorization, queue/noise expectations |
| Packaging | qccp page not integrated, local API missing, route mismatch |
| Scope | requested feature outside `delivery_profile`, timeline or data access change |
| Misunderstanding | stakeholder missed a documented limitation or artifact |

### Step 2: Gather Evidence

Read the relevant artifacts before answering:

- `application_manifest.json`
- `baseline_report.json`
- `quantum_report.json`
- `verification_report.md`
- `README.md` / `INTEGRATE.md`
- validation output
- command logs or screenshots when relevant

If evidence is absent, say so plainly and propose the smallest next check.

### Step 3: Choose Position

Use one of four positions:

- **Confirm**: the package already addresses the concern; cite the artifact.
- **Clarify**: the concern comes from ambiguous wording; rewrite the boundary.
- **Concede and fix**: the concern is valid and a concrete fix is planned.
- **Concede and scope out**: the concern is valid but outside the selected profile or current authorization.

Do not use "future work" to hide a blocker that invalidates the current claim.

### Step 4: Draft the Response

Recommended structure:

```markdown
Thanks for flagging this. Our current evidence supports [specific supported claim], not [unsupported stronger claim].

Evidence:
- [artifact/metric/path]
- [validation or command result]

Boundary:
- [simulator/cloud/hardware/data/profile limitation]

Next action:
- [fix, validation, scope decision, or no change]
```

For customer-facing replies, keep it short and concrete. For internal replies, include exact file paths and commands.

## Common Concerns

| Concern | Good response direction |
|---------|-------------------------|
| "Is this quantum advantage?" | Only say yes if fair baseline evidence supports it; otherwise say it demonstrates a quantum workflow or candidate route |
| "Why no real hardware?" | State authorization/credentials/queue/noise/cost boundary and whether hardware is in scope |
| "Baseline is too weak" | Concede if true; propose a stronger baseline and rerun comparison |
| "qccp page is missing" | Tie answer to `delivery_profile`; if profile requires it, mark package blocked |
| "Metric improved but app is not usable" | Separate algorithm evidence from packaging readiness |
| "Can we deploy now?" | Require validator, integration notes, credential handling, and selected profile evidence |

## Handoff

| Response outcome | Next skill | Payload |
|------------------|------------|---------|
| Needs artifact fix | `application-pipeline` | concern and required stage gate |
| Needs root-cause analysis | `application-debugging` | failing evidence or mismatch |
| Needs doc rewrite | `delivery-writing` | approved position and wording boundary |
| Needs package rereview | `delivery-review` | updated docs/artifacts |
| Needs demo update | `showcase-slides` | corrected supported claim |

## Reference Navigation

| Topic | Reference File | Use |
|-------|---------------|-----|
| Response tactics | `references/rebuttal-tactics.md` | Adapt tactics to stakeholder objections |
| Response template | `assets/rebuttal-template.md` | Optional response scaffold |
