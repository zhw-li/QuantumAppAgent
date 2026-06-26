---
name: qccp-service
description: "Guides qccp-service backend/API/deployment artifacts for the CT TianYan Quantum Computing Cloud Platform and quantum application cloud showcases. Use when working on Java/Spring Cloud modules, Controller/Service/Mapper/XML changes, Feign contracts, Nacos/bootstrap config, security/current-user rules, Maven verification, backend API wrapping, deployment config, health checks, or backend evidence for experiment-pipeline application packaging. Do NOT use for qccp frontend pages, UI design specs, cqlib algorithm work, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: EvoScientist
  version: '1.0.0'
  tags: [backend, qccp, service, api, cloud-showcase]
---

# qccp-service Backend

Use this skill as the concise backend entrypoint. Load only the reference file needed for the current task.

## When to Use

- User needs qccp-service compatible backend/API/deployment artifacts for a quantum application or cloud showcase.
- User asks for Controller/Service/Mapper/XML, Feign, config, security/current-user, Maven verification, endpoint contract, or health-check guidance.
- `experiment-pipeline` Stage 3 needs backend or deployment packaging evidence.

## When NOT to Use

- **Frontend page, route, or i18n output** -> use `qccp-ui` and `qccp-frontend`.
- **Quantum algorithm implementation or simulator/cloud circuit execution** -> use `cqlib-sdk` and algorithm skills.
- **Planning only or final verification** -> use `paper-planning` or `experiment-pipeline`.

## First steps

1. Confirm the active repository is `qccp-service` or that the requested output is a qccp-service-compatible artifact.
2. Read the root `pom.xml`, target module `pom.xml`, application class, and nearby Controller/Service/Mapper/XML files before editing.
3. Locate the owner module by business keywords, endpoint paths, class names, table names, permission keys, and Feign names.
4. Keep diffs narrow. Modify `qccp-api` or `qccp-common` only when the contract or utility is genuinely shared.
5. Never commit secrets, Nacos credentials, certificates, private endpoints, logs, generated temp files, or IDE config.

## Reference routing

- `references/project-map.md`: repository identity, stack, module responsibilities, module routing, and key files.
- `references/backend-coding-rules.md`: Java layout, Controller, Service, Mapper/XML, response model, file-stream, logging, and style rules.
- `references/feign-and-config.md`: Feign contracts, cross-service headers, Nacos/bootstrap config, and qccp-ctyun AI assistant paths.
- `references/security-and-commands.md`: current-user/security rules, safe edit workflow, search commands, Maven commands, and verification reporting.

## Backend workflow

1. Determine module ownership using `references/project-map.md`.
2. Inspect existing call chain:
   `controller -> service/service.impl -> mapper -> resources/mapper/*.xml -> domain/dto/vo`.
3. Design the smallest API contract that satisfies the caller and follows local response wrappers.
4. Implement within the target module's naming, package, injection, exception, and logging style.
5. If SQL is involved, update both Mapper interface and XML together.
6. If Feign is involved, update the interface, fallback factory, provider Controller, and callers together.
7. If config is involved, follow the existing Nacos/profile path and keep secrets external.
8. Run the smallest relevant Maven command from `references/security-and-commands.md`.

## Application delivery handoff

For quantum application delivery, backend work contributes app packaging and verification evidence. Provide:

- endpoint paths, methods, request/response schema, and error cases
- service boundaries and persistence or job-execution ownership
- required environment variables or ignored local config keys
- health-check and build/test commands
- contract evidence for `experiment-pipeline` when frontend/backend integration is in scope

Do not decide delivery readiness from this skill. Provide reviewable backend/API evidence for the application packaging and verification stages.

## Completion checklist

- [ ] Target module and call chain are confirmed.
- [ ] Response wrapper and permission/log annotations match local precedent.
- [ ] Mapper and XML stay synchronized when SQL changes.
- [ ] Feign provider, interface, fallback, and callers stay synchronized when contracts change.
- [ ] Secrets and environment-specific values remain outside code and docs.
- [ ] The smallest relevant Maven verification command is reported.
