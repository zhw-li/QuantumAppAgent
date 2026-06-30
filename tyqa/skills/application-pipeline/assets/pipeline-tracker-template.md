# Experiment Pipeline Tracker

## Project Info

- **Project**: [Quantum application project name]
- **Application Goal**: [One-sentence description]
- **Start Date**: [YYYY-MM-DD]
- **Source**: [Link to research proposal from application-intake, if applicable]

## Pipeline Status

| Stage | Status | Skill Used | Attempts Used | Budget | Gate Met? |
|-------|--------|------------|---------------|--------|-----------|
| 1. Application Scope & Baseline | [ ] Not started / [ ] In progress / [ ] Complete | [delivery-planning, application-pipeline] | 0 / 10 | <=10 | [ ] |
| 2. Quantum Method Implementation | [ ] Not started / [ ] In progress / [ ] Complete | [cqlib-sdk + algorithm skill] | 0 / 12 | <=12 | [ ] |
| 3. Application Packaging | [ ] Not started / [ ] In progress / [ ] Complete | [qccp-ui, qccp-frontend, qccp-service] | 0 / 8 | <=8 | [ ] |
| 4. Verification & Handoff | [ ] Not started / [ ] In progress / [ ] Complete | [delivery-writing, delivery-review, showcase-slides] | 0 / 6 | <=6 | [ ] |

**Total Attempts**: 0 / 36

## Stage Details

### Stage 1: Application Scope & Baseline
- **Requirements**: [`requirements.json` path]
- **Primary Metric**: [metric + direction]
- **Baseline Result**: [`baseline_report.json` summary]
- **Status Notes**: [Brief notes]

### Stage 2: Quantum Method Implementation
- **Algorithm Route**: [cqlib-qaoa / cqlib-vqe / cqlib-qml / cqlib-hybrid]
- **Quantum Result**: [`quantum_report.json` summary]
- **Comparability**: [same data/metric/backend assumptions?]
- **Status Notes**: [Brief notes]

### Stage 3: Application Packaging
- **Frontend Evidence**: [qccp page path/build notes]
- **Backend Evidence**: [API/service/deployment notes]
- **Integration Status**: [Which components are integrated]
- **Status Notes**: [Brief notes]

### Stage 4: Verification & Handoff
- **Verification Report**: [`verification_report.md` path]
- **Delivery Docs**: [`README.md` / `INTEGRATE.md` / slides path]
- **Claim Boundary**: [simulator/cloud/real-hardware wording]
- **Status Notes**: [Brief notes]

## Backtracking Log

Record any stage regressions (e.g., discovering a Stage 1 issue during Stage 3):

| Date | From Stage | To Stage | Reason | Resolution |
|------|-----------|----------|--------|------------|
| | | | | |

## Cross-Stage Insights

- [Insight 1 that spans multiple stages]
- [Insight 2]

## Results Summary

| Artifact/Method | Primary Metric | Secondary Metric 1 | Secondary Metric 2 | Evidence Path |
|-----------------|---------------|--------------------|--------------------|---------------|
| Classical baseline | [value] | [value] | [value] | [path] |
| Quantum method | [value] | [value] | [value] | [path] |
| App packaging | [build/check] | [API check] | [deployment note] | [path] |

## Evolution Memory Triggers

- [ ] Pipeline succeeded → Trigger ESE (Experiment Strategy Evolution)
- [ ] No executable code within budget, or method underperforms baseline → Trigger IVE (Idea Validation Evolution)
- [ ] Evolution report written to `/memory/evolution-reports/`

## Handoff Checklist

- [ ] All stage logs complete
- [ ] Trajectory logs saved
- [ ] Skill Used values recorded in tracker and stage logs
- [ ] Results tables ready for delivery-writing
- [ ] README, INTEGRATE, verification report, and slides notes ready
- [ ] Key implementation details documented
- [ ] application-memory updated
