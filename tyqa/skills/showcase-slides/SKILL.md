---
name: showcase-slides
description: "Guides creation or refinement of quantum application showcase slides: PoC demo narrative, Cqlib algorithm explanation, baseline-vs-quantum evidence, qccp/cloud workflow, validation boundary, limitations, and stakeholder Q&A. Use when the user needs slide structure, demo flow, visual hierarchy, speaker notes, or .pptx generation from application artifacts. Do NOT use for writing README/reports (use delivery-writing), implementing qccp pages (use qccp-ui/qccp-frontend), or generating standalone visuals without a slide narrative (use nano-banana)."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '3.0.0'
  tags: [core, quantum-application, showcase, presentation]
---

# Showcase Slides

Build a presentation around a working or planned quantum application. The deck should make the demo understandable without overstating the evidence.

## When to Use This Skill

- User needs PoC/demo slides for a quantum application.
- User wants to explain a Cqlib algorithm route, baseline comparison, and validation outcome.
- User needs qccp/cloud showcase narrative, speaker notes, or backup Q&A.
- User wants to turn README, verification report, or app screenshots into a deck.
- User asks for a concise presentation for customers, internal review, or technical handoff.

## When NOT to Use

- Writing README, INTEGRATE, or verification report -> use `delivery-writing`.
- Reviewing delivery readiness -> use `delivery-review`.
- Implementing frontend/backend artifacts -> use `qccp-ui`, `qccp-frontend`, or `qccp-service`.
- Generating a standalone image asset -> use `nano-banana` or image generation.

## Before You Start

Answer three questions:

1. **Audience**: customer, engineering team, leadership, or technical review?
2. **Supported claim**: what do the artifacts actually prove?
3. **Demo path**: algorithm-only, local FastAPI demo, qccp-web page, or full delivery?

If the evidence is incomplete, design the deck around the current boundary rather than hiding gaps.

## Core Workflow

### Step 1: Read Source Artifacts

Use:

- `application_manifest.json`
- `requirements.json`
- `baseline_report.json`
- `quantum_report.json`
- `verification_report.md`
- README/INTEGRATE
- screenshots, figures, or qccp/local demo assets

### Step 2: Draft Narrative Arc

Recommended structure:

1. Problem and user workflow
2. Why the baseline matters
3. Quantum route and Cqlib implementation
4. Result comparison and validation evidence
5. Demo surface: local/qccp/cloud workflow
6. Limitations and next validation step
7. Q&A backup: baseline fairness, hardware boundary, deployment scope

### Step 3: Design Slide Breakdown

Keep slides evidence-first:

| Slide | Purpose |
|-------|---------|
| Title | application name and supported claim |
| Workflow | input -> quantum/classical processing -> output |
| Baseline | comparator and metric |
| Quantum method | encoding, circuit/model, backend |
| Results | baseline vs quantum, metric direction, limitations |
| Demo | UI/API/qccp flow and screenshots |
| Validation | validator result and blockers |
| Next steps | concrete remaining work |
| Backup | stakeholder concerns and answers |

### Step 4: Build Slides

Use the repository's existing presentation tooling if available. If creating `.pptx`, keep text concise and place detailed evidence in speaker notes or backup slides.

### Step 5: Rehearse Claims

For each slide, check:

- Does the title make a claim supported by artifacts?
- Are metric values identical to reports?
- Is simulator/cloud/hardware status visible where needed?
- Are limitations stated before likely objections?
- Is the demo route reproducible from README/INTEGRATE?

## Artifact Sources from Other Skills

| Source Skill | Artifact | Use In Slides |
|--------------|----------|---------------|
| `application-intake` | application brief and route card | motivation and scope |
| `delivery-planning` | manifest, route, validation plan | method and artifact map |
| `application-pipeline` | reports, app evidence, validator output | results and readiness |
| `delivery-writing` | README, verification report | slide copy and speaker notes |
| `delivery-review` | findings and risk list | backup Q&A and limitations |

## Claim Rules

1. Lead with the application and workflow, not a generic quantum pitch.
2. Show the baseline comparison before any advantage language.
3. Never let a slide imply real-hardware validation when only simulator evidence exists.
4. Use one limitation slide or callout; do not bury blockers in Q&A.
5. Keep qccp/local/API screenshots tied to the selected `delivery_profile`.

## Reference Navigation

| Topic | Reference File | When to Use |
|-------|---------------|-------------|
| Talk structures | `references/talk-structure.md` | Organizing the narrative arc |
| Slide design | `references/slide-design.md` | Visual hierarchy and layout rules |
| Slide creation | `references/slide-creation.md` | Building .pptx files with code |
| Delivery and Q&A | `references/delivery-and-qa.md` | Rehearsal and stakeholder questions |
| Talk outline template | `assets/talk-outline-template.md` | Starting a deck |
