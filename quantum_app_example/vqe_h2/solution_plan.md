# Engineering Plan: H2 VQE

1. **Scientific specification.** Freeze geometry, Hamiltonian, energy convention, bit order, baseline, oracle and acceptance threshold.
2. **Cqlib realization.** Construct the HF initial state and one-parameter particle-conserving ansatz; evaluate Pauli expectations with the statevector backend.
3. **Application system.** Expose reference, VQE and comparison endpoints; present the same fields in the standalone page and QCCP page.
4. **Validation.** Check public reference values, dense-matrix equivalence, variational behavior, three initialization seeds, API schemas and generated reports.
5. **Evidence boundary.** Label all results as simulator evidence for a fixed two-qubit instance and prohibit hardware or quantum-advantage claims.
