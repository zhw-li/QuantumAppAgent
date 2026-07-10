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
- For generated local demos, use a single-origin service: the same FastAPI process serves `/`, `/static/*`, and `/api/*` on the configured generated-app bind port from `application_manifest.json.network`.
- Frontend JavaScript must call relative API paths such as `/api/solve`; do not hardcode `localhost`, `127.0.0.1`, `10.9.1.8`, or any full backend domain in frontend source.
- The local demo UI must use the `qccp-ui` standalone visual profile: Chinese-first copy, qccp token colors/typography/spacing/radius, vertical cloud-showcase layout, no emoji, and no generic English demo labels such as "Run Baseline". Keep it standalone; do not depend on qccp-web runtime imports.
- Use `Path(__file__).resolve()` based paths, not shell working-directory assumptions.
- Missing `frontend/index.html` or `frontend/static` is a startup/configuration error; do not silently create empty frontend directories or skip static mounting.
- Record each static asset mapping in `application_manifest.json` under `local_demo.static_assets` as URL plus actual file path so validation can request or inspect the referenced CSS/JS.
- Use `static_assets: []` only for a self-contained single-file HTML demo with no `/static/...` references. Otherwise each item must be an object such as `{"url": "/static/style.css", "path": "frontend/static/style.css"}`; never use bare strings.
- Core runtime libraries for the local demo should be vendored under `frontend/static/vendor/`; do not rely on CDN-hosted Chart.js, ECharts, Vue, or similar runtime dependencies for a deliverable demo.
- Record `application_manifest.json.network` with `mode`, `bind_host`, `bind_port`, `public_scheme`, `public_host`, `public_port`, `public_base_url`, `api_base`, and `frontend_serving`. Use the configured generated-app network contract rather than inventing a port.
- Record `local_demo.ui_profile = "qccp-ui-standalone"` and `local_demo.language = "zh-CN"`.
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
APP_BIND_HOST=<network.bind_host> APP_BIND_PORT=<network.bind_port> python backend/main.py
uvicorn backend.main:app --host <network.bind_host> --port <network.bind_port>
curl -s <network.public_base_url>/health
```

If the app has targeted tests or smoke scripts, run those first. Report the command, result, and any missing dependency or port conflict.

## Handoff evidence

For `application-pipeline` application packaging evidence, provide:

- backend entry point and run command
- health-check result or reproduction command
- endpoint contract and sample request/response
- `application_manifest.json` updates for `network`, `local_demo.backend_entrypoint`, `local_demo.entrypoint`, endpoints, static assets, and verification commands
- `local_demo.ui_profile` and `local_demo.language` evidence
- single-origin frontend/backend public URL from `network.public_base_url`
- environment variables and ignored config keys
- README, INTEGRATE, and verification report paths when in scope

Do not decide final delivery readiness from this path. Provide backend/API evidence for the verification stage.
