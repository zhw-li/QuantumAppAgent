---
name: qccp-service
description: "Guides backend/API/deployment artifacts for CT TianYan Quantum Computing Cloud Platform cloud showcases. Use for Python FastAPI quantum app service packaging by default, or for Java/Spring Cloud qccp-service integration when the repo/request explicitly targets qccp-service modules, Controller/Service/Mapper/XML changes, Feign contracts, Nacos/bootstrap config, Maven verification, health checks, or backend evidence for application-pipeline application packaging. Do NOT use for qccp frontend pages, UI design specs, cqlib algorithm work, or final delivery readiness decisions."
allowed-tools: "write_file edit_file read_file think_tool execute"
metadata:
  author: TYQA
  version: '1.0.0'
  tags: [backend, qccp, service, api, cloud-showcase]
---

# qccp-service Backend and Local Demo Dispatcher

Use this skill as the owner of backend/API contracts and the `local_fastapi_demo` delivery profile. First choose the backend path, then load only the reference file needed for the current task.

## When to Use

- User needs backend/API/deployment artifacts for a quantum application or cloud showcase.
- User is packaging a local Python FastAPI quantum app service with health checks, API contracts, local HTML/static demo hosting, or INTEGRATE evidence.
- User explicitly targets Java/Spring Cloud qccp-service modules, Controller/Service/Mapper/XML, Feign, config, security/current-user, Maven verification, endpoint contract, or health-check guidance.
- `application-pipeline` Stage 3 needs backend or deployment packaging evidence.

## When NOT to Use

- **qccp-web Vue SFC page, route, or i18n output** -> use `qccp-ui` and `qccp-frontend`.
- **Quantum algorithm implementation or simulator/cloud circuit execution** -> use `cqlib-sdk` and algorithm skills.
- **Planning only or final verification** -> use `delivery-planning` or `application-pipeline`.

## Backend path selection

1. **Python FastAPI quantum app service (default)**: use when the task is a local quantum application backend, demo API, static frontend service, `/health` endpoint, `/api/info`, `/api/solve`, `/api/predict`, deployment note, or INTEGRATE handoff.
2. **Java qccp-service integration**: use only when the active repository is `qccp-service`, the files are Java/Spring Cloud/POM/Mapper/XML/Nacos/Feign files, or the user explicitly asks for qccp-service-compatible Java integration.
3. If the task mixes both, keep the FastAPI app service as the demonstrable local backend and document the Java qccp-service integration boundary separately.
4. Never silently rewrite a Python FastAPI sample into Java. Never silently fall back from Java qccp-service integration to a simulator or local demo when real platform integration is requested.
5. Never commit secrets, Nacos credentials, cloud tokens, certificates, private endpoints, logs, generated temp files, or IDE config.

## Reference routing

- `references/fastapi-service.md`: Python FastAPI app service packaging, endpoint contract, static frontend hosting, config, verification, and INTEGRATE evidence.
- `references/java-qccp-service.md`: Java qccp-service integration workflow and links to Java-specific module, coding, Feign/config, security, and Maven rules.
- `references/project-map.md`: Java qccp-service repository identity, stack, module responsibilities, module routing, and key files.
- `references/backend-coding-rules.md`: Java layout, Controller, Service, Mapper/XML, response model, file-stream, logging, and style rules.
- `references/feign-and-config.md`: Java Feign contracts, cross-service headers, Nacos/bootstrap config, and qccp-ctyun AI assistant paths.
- `references/security-and-commands.md`: Java current-user/security rules, safe edit workflow, search commands, Maven commands, and verification reporting.

## Backend workflow

1. Select the backend path from the evidence in the request and repository.
2. Read the relevant reference file before editing.
3. Read `application_manifest.json` when it exists; otherwise define the smallest API contract needed by the selected delivery profile.
4. For `local_fastapi_demo`, record backend endpoints in `local_demo`: endpoint path, method, request schema, response schema, error cases, sample request when needed, static asset mappings, backend entry point, local demo entrypoint, and verification command.
5. Keep algorithm execution, backend service wrapping, frontend display schema, deployment notes, and verification evidence separate.
6. Run the smallest relevant local verification command for the selected path.

## Application delivery handoff

For quantum application delivery, backend work contributes app packaging and verification evidence. Provide:

- endpoint paths, methods, request/response schema, and error cases
- `application_manifest.json` `local_demo` contract updates when the manifest exists
- service boundaries and persistence or job-execution ownership
- required environment variables or ignored local config keys
- health-check and build/test commands for the selected backend path
- contract evidence for `application-pipeline` when frontend/backend integration is in scope

Do not decide delivery readiness from this skill. Provide reviewable backend/API evidence for the application packaging and verification stages.

## Completion checklist

- [ ] Backend path is explicitly identified as Python FastAPI or Java qccp-service.
- [ ] Endpoint contract and error cases are documented.
- [ ] `local_demo` contract is recorded in `application_manifest.json` when the application manifest is in scope.
- [ ] Health check and smallest relevant verification command are reported.
- [ ] Frontend/backend integration evidence is captured when in scope.
- [ ] Java module/call chain is confirmed before Java edits.
- [ ] Mapper/XML and Feign/provider/caller files stay synchronized when Java contracts change.
- [ ] Secrets and environment-specific values remain outside code and docs.
