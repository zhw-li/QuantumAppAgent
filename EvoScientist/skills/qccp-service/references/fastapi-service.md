# Python FastAPI Quantum App Service

Use this path for local quantum application services, runnable demos, and cloud-showcase handoff artifacts that are not being implemented inside the Java `qccp-service` repository.

## Service shape

- Keep the quantum algorithm code separate from the FastAPI route layer.
- Prefer a small `backend/main.py` or equivalent service entry point.
- Expose a health endpoint, usually `GET /health`, that does not run expensive quantum computation.
- Expose app metadata through `GET /api/info` when the frontend or INTEGRATE notes need capability discovery.
- Expose the primary task through a stable endpoint such as `POST /api/solve`, `POST /api/predict`, or a domain-specific route already used by the sample.
- Validate request payloads and return explicit 4xx errors for invalid inputs.
- Keep long-running, stochastic, or hardware-backed execution clearly labeled in responses and docs.

## API contract

Document each endpoint with:

- method and path
- request schema, including required and optional fields
- response schema, including `status`, result fields, metadata, and error fields when used
- backend assumptions such as simulator, shots, seed, model path, and data source
- known limitations and expected runtime

Do not invent platform-only fields such as `apiCode`, device IDs, tenant IDs, or internal gateway headers unless they already exist in the target integration docs or the user provides them.

## Static frontend and local demo

- If FastAPI serves a static frontend, mount static assets explicitly and keep paths consistent with the HTML or Vue output.
- Prefer local demo ports documented in the app README or solution plan; avoid changing ports unless there is a conflict.
- Keep qccp-web SFC output separate from the local FastAPI demo frontend.
- Do not claim the SFC is integrated into qccp-web unless the target qccp-web repository was actually modified and verified.

## Configuration and secrets

- Use environment variables or ignored local config for tokens, cloud credentials, model paths, data paths, and platform endpoints.
- Do not paste API keys, tokens, private endpoints, cloud account identifiers, or Nacos credentials into code, docs, tests, or logs.
- Do not silently fall back from real hardware or cloud execution to local simulation.

## Verification commands

Use the smallest command that proves the changed surface:

```bash
python -m pytest
python backend/main.py
uvicorn backend.main:app --host 0.0.0.0 --port <port>
curl -s http://127.0.0.1:<port>/health
```

If the app has targeted tests or smoke scripts, run those first. Report the command, result, and any missing dependency or port conflict.

## Handoff evidence

For `experiment-pipeline` application packaging evidence, provide:

- backend entry point and run command
- health-check result or reproduction command
- endpoint contract and sample request/response
- frontend/backend base URL or proxy expectation
- environment variables and ignored config keys
- README, INTEGRATE, and verification report paths when in scope

Do not decide final delivery readiness from this path. Provide backend/API evidence for the verification stage.
