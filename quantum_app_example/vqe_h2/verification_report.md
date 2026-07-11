# Verification Report: H2 VQE Reference Application

## Result

| Check | Result |
|---|---|
| Scientific and API contract tests | 13 passed |
| FastAPI import check | passed |
| TYQA artifact and packaging validator | passed, no blockers |
| Seeds | 42, 123, 456 |
| Maximum VQE error | < 1e-9 mHa |
| Chemical-accuracy gate | passed for all seeds |
| Execution backend | `cqlib.StatevectorSimulator` |

## Scientific Values

| Quantity | Value (Ha) |
|---|---:|
| HF electronic energy | -1.836967991203 |
| Exact electronic energy | -1.857275030202 |
| Nuclear repulsion | 0.719968994449 |
| HF total energy | -1.116998996754 |
| Exact total energy | -1.137306035753 |

The tests independently verify Hamiltonian assembly, Cqlib endianness, HF initialization, circuit expectation values, the variational bound, report schemas and API fields. The generic TYQA validator separately checks artifact presence, manifest and network schemas, backend routes, local smoke behavior, QCCP source contracts, documentation consistency, and packaging. The current environment emits one Starlette deprecation warning from `TestClient`; it does not affect the tested behavior.

## Interpretation Boundary

These results establish internal consistency for one fixed H2 instance under exact statevector simulation. They do not establish quantum advantage or performance on cloud simulators and quantum processors.
