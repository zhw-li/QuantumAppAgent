# Python FastAPI Quantum App Service

Use this path for local quantum application services, runnable demos, and the `local_fastapi_demo` delivery profile when the app is not being implemented inside the Java `qccp-service` repository.

## Service shape

- Keep the quantum algorithm code separate from the FastAPI route layer.
- Prefer a small `backend/main.py` or equivalent service entry point.
- Expose a health endpoint, usually `GET /health`, that does not run expensive quantum computation.
- Expose app metadata through `GET /api/info` when the frontend or INTEGRATE notes need capability discovery.
- Expose the primary task through a stable endpoint such as `POST /api/solve`, `POST /api/predict`, or a domain-specific route already used by the sample.
- Validate request payloads and return explicit 4xx errors for invalid inputs.
- Keep long-running, stochastic, or hardware-backed execution clearly labeled in responses and docs.

## API contract

Document each endpoint and, when `application_manifest.json` is in scope, record the same contract under `backend.endpoints`:

- method and path
- request schema, including required and optional fields
- response schema, including `status`, result fields, metadata, and error fields when used
- backend assumptions such as simulator, shots, seed, model path, and data source
- known limitations and expected runtime

Do not invent platform-only fields such as `apiCode`, device IDs, tenant IDs, or internal gateway headers unless they already exist in the target integration docs or the user provides them.

## Static frontend and local demo

- Local demo layout is `frontend/index.html` plus `frontend/static/` for CSS, JS, and local vendor libraries.
- Mount `/static` to the actual `frontend/static` directory and serve `/` from `frontend/index.html`.
- Use `Path(__file__).resolve()` based paths, not shell working-directory assumptions.
- Missing `frontend/index.html` or `frontend/static` is a startup/configuration error; do not silently create empty frontend directories or skip static mounting.
- Record each static asset mapping in `application_manifest.json` under `local_demo.static_assets` as URL plus actual file path so validation can request or inspect the referenced CSS/JS.
- Core runtime libraries for the local demo should be vendored under `frontend/static/vendor/`; do not rely on CDN-hosted Chart.js, ECharts, Vue, or similar runtime dependencies for a deliverable demo.
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
- `application_manifest.json` updates for `local_demo.backend_entrypoint`, `local_demo.entrypoint`, endpoints, static assets, and verification commands
- frontend/backend base URL or proxy expectation
- environment variables and ignored config keys
- README, INTEGRATE, and verification report paths when in scope

Do not decide final delivery readiness from this path. Provide backend/API evidence for the verification stage.
