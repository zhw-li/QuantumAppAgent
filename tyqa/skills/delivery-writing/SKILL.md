---
name: delivery-writing
description: "Guides writing quantum application delivery documents: README.md, INTEGRATE.md, verification_report.md, customer/engineering handoff notes, algorithm explanation, baseline-vs-quantum comparison, limitation statements, and cloud showcase narrative. Use when verified artifacts need clear delivery wording. Do NOT use for executing validation (use application-pipeline), package self-review (use delivery-review), early route planning (use delivery-planning), or slide-deck structure (use showcase-slides)."
allowed-tools: "write_file edit_file read_file think_tool"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, delivery-writing, docs]
---

# Delivery Writing

Write handoff materials that match the actual quantum application artifacts. The main job is evidence alignment: numbers, claims, commands, API paths, and limitations must agree with the manifest and reports.

## When to Use This Skill

- User needs `README.md`, `INTEGRATE.md`, `verification_report.md`, release notes, or customer-facing PoC explanation.
- Application artifacts already exist or are being finalized.
- User needs a baseline-vs-quantum comparison written without overclaiming.
- User needs to explain Cqlib algorithm design, qccp integration, simulator/cloud boundary, or validation limitations.
- User asks for handoff text after `application-pipeline`.

## When NOT to Use

- Executing stages or producing reports from code -> use `application-pipeline`.
- Planning artifact contracts -> use `delivery-planning`.
- Reviewing package readiness -> use `delivery-review`.
- Creating slides -> use `showcase-slides`.
- Searching external evidence -> use `evidence-navigator`.

## Required Inputs

Prefer reading these artifacts directly:

- `application_manifest.json`
- `requirements.json`
- `baseline_report.json`
- `quantum_report.json`
- `verification_report.md` if already started
- qccp/local API and frontend evidence
- command logs and limitations

If an artifact is missing, write the gap as a limitation or blocker. Do not invent a number, path, dataset, cloud backend, or hardware result.

## Document Types

### README.md

Include:

1. application purpose and user workflow
2. requirements and setup
3. baseline command and result
4. quantum method command and result
5. how to run the selected delivery profile
6. validation command
7. limitations and unsupported claims

### INTEGRATE.md

Include:

1. selected `delivery_profile`
2. file copy destinations or route snippets
3. API request/response schema
4. qccp-web route/component notes when relevant
5. local FastAPI run command when relevant
6. environment variables and credentials policy
7. build/test evidence

### verification_report.md

Include:

1. artifact inventory
2. baseline-vs-quantum comparability
3. metric values and `higher_is_better`
4. validator result
5. packaging evidence by layer
6. blockers and limitations
7. final readiness boundary

### Showcase Narrative

Write concise demo copy:

- what problem the app solves
- what the user uploads or selects
- what the quantum route computes
- what evidence supports the result
- what is simulator-only or not yet hardware-validated

## Claim Rules

1. Never describe simulator evidence as real-hardware performance.
2. Never claim quantum advantage unless the reports support it with a fair baseline.
3. Prefer "demonstrates a quantum workflow" over "proves superiority" when evidence is limited.
4. Include one meaningful limitation in every external-facing report.
5. Keep metric names and values identical to the JSON reports.
6. If validation failed, write "not release-ready" or "blocked by..." rather than soften the failure.

## Artifact Sources

| Source Skill | Artifact | Use |
|--------------|----------|-----|
| `delivery-planning` | manifest, requirements, solution/validation plan | structure docs |
| `application-pipeline` | baseline/quantum reports, app evidence, validator result | main evidence |
| `application-debugging` | failure cause and fix | limitations and troubleshooting |
| `qccp-frontend` / `qccp-service` | UI/API/deployment evidence | INTEGRATE and demo docs |
| `delivery-review` | claim and evidence findings | final revisions |

## Handoff

| Next step | Target skill | Payload |
|-----------|--------------|---------|
| Review claims and completeness | `delivery-review` | docs plus source artifacts |
| Build demo deck | `showcase-slides` | README, verification report, figures/screenshots |
| Resume execution | `application-pipeline` | missing artifacts or blockers |
| Capture reusable lesson | `application-memory` | validated pattern or failure mode |

## Reference Navigation

Existing writing references may still be useful for structure and clarity, but adapt them to delivery docs:

| Topic | Reference File | Use |
|-------|---------------|-----|
| concise structure | `references/writing-principles.md` | paragraph clarity |
| method explanation | `references/method-templates.md` | algorithm section scaffolding |
| results wording | `references/experiments-guide.md` | comparison narrative |
| limitations | `references/supplementary-guide.md` | extra evidence and caveats |
