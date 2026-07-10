# Validation Plan — VQE H2

## Baseline vs Quantum Comparability
- Same Hamiltonian (same Pauli terms, same coefficients, same qubit mapping)
- Same metric: energy_error (mHartree, lower_is_better)
- Same reference: exact diagonalization ground-state energy
- Both compute on the same 2-qubit system

## Primary Metric
- **Name**: energy_error
- **Definition**: |E_quantum - E_exact| × 1000 (mHartree)
- **Direction**: lower_is_better
- **Threshold**: ≤ 1.6 mHartree (chemical accuracy)
- **Success**: VQE energy_error ≤ baseline energy_error (baseline is ~0 by definition for exact diagonalization)

## Validation Commands
1. `cd /code/cqlib_app/vqe_h2 && python -m algorithms.baseline` → baseline_report.json
2. `cd /code/cqlib_app/vqe_h2 && python -m algorithms.vqe` → quantum_report.json
3. `cd /code/cqlib_app/vqe_h2 && python -m app.main --check` → API health check
4. `validate_quantum_application(app_dir="/code/cqlib_app/vqe_h2")`

## Seeds
Multiple seeds for VQE: [42, 123, 456] — report mean and std of energy_error across seeds.

## Blockers
- VQE fails to converge → increase layers or switch optimizer
- Hamiltonian coefficients incorrect → verify against exact diagonalization
- API/frontend contract mismatch → check manifest network config
- validate_quantum_application blockers → fix per layer

## Simulator vs Hardware Caveat
All results are simulator-only. Do not describe as real-hardware performance.
