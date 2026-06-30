---
name: delivery-review
description: "Guides adversarial self-review of a quantum application delivery package: manifest/report consistency, baseline-vs-quantum comparability, validation blockers, qccp/local packaging evidence, simulator-vs-hardware claim boundaries, README/INTEGRATE completeness, and unsupported customer-facing statements. Use before handoff or demo. Do NOT use for writing first drafts (use delivery-writing), executing fixes (use application-pipeline), or responding to external feedback (use stakeholder-response)."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, delivery-review, validation]
---

# Delivery Review

Review the delivery package as a skeptical engineer, customer, and validation gate would. Findings should be concrete, file/path-based, and tied to artifacts.

## When to Use This Skill

- User asks whether a quantum application package is ready for handoff.
- README, INTEGRATE, reports, or slides need evidence consistency review.
- `application_manifest.json`, `baseline_report.json`, and `quantum_report.json` may disagree.
- The package includes simulator/cloud/hardware claims that need boundary checks.
- qccp/local demo artifacts need completeness review before sharing.

## When NOT to Use

- Writing the first version of docs -> use `delivery-writing`.
- Running baseline/quantum/app fixes -> use `application-pipeline`.
- Debugging a specific failed command -> use `application-debugging`.
- Responding to customer or reviewer feedback -> use `stakeholder-response`.

## Prerequisites

Read the actual artifacts when available:

- `application_manifest.json`
- `requirements.json`
- `baseline_report.json`
- `quantum_report.json`
- `verification_report.md`
- `README.md`
- `INTEGRATE.md`
- qccp/local service and frontend files

Do not review only the prose if structured artifacts exist.

## Review Checklist

### 1. Contract Consistency

- Manifest paths point to real artifacts.
- `delivery_profile` matches the implemented layers.
- Required fields exist for the selected profile.
- Validation commands are runnable or clearly marked unavailable.
- Artifact names and directories are consistent across docs.

### 2. Baseline-vs-Quantum Evidence

- Baseline and quantum reports use the same task, dataset/split, metric, and `higher_is_better`.
- Metric values are copied exactly.
- Backend, shots, seed, and simulator/cloud/hardware status are stated.
- Runtime or cost comparisons are not implied unless measured.
- Negative or weak results are not hidden.

### 3. Packaging Evidence

- `algorithm_only`: code and reports are enough for review.
- `local_fastapi_demo`: endpoint schema, run command, static/demo assets, and local check are present.
- `qccp_web_page`: Vue SFC/route/style/API contract are present and use manifest paths.
- `full_delivery`: local demo, qccp page, docs, and verification all align.

### 4. Claim Boundaries

- No unsupported "quantum advantage" language.
- No simulator result presented as real hardware.
- No hidden credential, endpoint, or user-specific path.
- Limitations are explicit and meaningful.
- Customer-facing text says what is demonstrated, not what is hoped.

### 5. Usability and Handoff

- README explains how to reproduce the key result.
- INTEGRATE explains where to place files and how to connect APIs/routes.
- Verification report names blockers by layer.
- Screenshots/figures/tables match the actual app state.
- A new engineer can rerun the minimal path without oral context.

## Output Format

Lead with findings:

```markdown
## Findings

| Severity | File/Artifact | Issue | Required Fix |
|----------|---------------|-------|--------------|
| High | ... | ... | ... |

## Readiness Verdict
[Ready / Ready with limitations / Blocked]

## Evidence Checked
[artifact list and commands if any]

## Residual Risk
[what remains uncertain]
```

Severity guide:

- **High**: invalid comparison, missing required artifact, false hardware/cloud claim, broken selected delivery profile.
- **Medium**: reproducibility gap, unclear limitation, stale path, incomplete integration instruction.
- **Low**: wording clarity, formatting, optional polish.

## Handoff

| Outcome | Next skill | Payload |
|---------|------------|---------|
| Docs need edits | `delivery-writing` | findings and target docs |
| Artifacts need fixes | `application-pipeline` | failed gate and required artifacts |
| Specific failure needs diagnosis | `application-debugging` | command/error/artifact mismatch |
| External concern needs answer | `stakeholder-response` | concern, evidence, proposed position |
| Demo material needed | `showcase-slides` | reviewed claims and evidence |

## Reference Navigation

| Topic | Reference File | Use |
|-------|---------------|-----|
| Review checklist | `references/review-checklist.md` | Extended checklist |
| Adversarial review | `references/counterintuitive-review.md` | Harder claim review |
