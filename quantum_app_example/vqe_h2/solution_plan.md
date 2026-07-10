# Solution Plan — VQE H2 Ground-State Energy

## Stage 1: Application Scope & Baseline
- **Goal**: Define requirements, implement classical exact diagonalization baseline
- **Success signals**: baseline_report.json with energy_error < 0.001 mHartree (exact diagonalization is numerically exact)
- **What to run**: `python -m algorithms.baseline`
- **Expected artifacts**: baseline_report.json

## Stage 2: Quantum Method Implementation
- **Goal**: Implement VQE with cqlib, compare against baseline
- **Success signals**: quantum_report.json with energy_error ≤ 1.6 mHartree (chemical accuracy)
- **What to run**: `python -m algorithms.vqe`
- **Expected artifacts**: quantum_report.json, convergence trace, circuit QCIS

## Stage 3: Application Packaging
- **Goal**: Build local FastAPI demo + qccp-web page
- **Success signals**: FastAPI serves both frontend and API on port 8080; qccp Vue SFC follows design spec
- **What to run**: `python -m app.main` for local demo
- **Expected artifacts**: app/main.py, app/static/index.html, qccp_page/VqeH2Page.vue

## Stage 4: Verification & Handoff
- **Goal**: Validate all artifacts, write documentation
- **Success signals**: validate_quantum_application passes; README, INTEGRATE, verification_report are consistent
- **What to run**: validate_quantum_application(app_dir="/code/cqlib_app/vqe_h2")
- **Expected artifacts**: verification_report.md, README.md, INTEGRATE.md
