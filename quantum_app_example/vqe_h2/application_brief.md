# Application Brief: H2 Ground-State Energy with VQE

## Objective

Realize and validate a platform-facing quantum application for one fixed H2 ground-state problem. The application must preserve one scientific contract from Hamiltonian definition through Cqlib execution, service responses and user-interface presentation.

## Fixed Scientific Instance

- H2 in the STO-3G basis at 0.735 angstrom;
- fixed two-qubit electronic Hamiltonian;
- Cqlib bitstring convention `|q1 q0>` and HF determinant `|01>`;
- molecular total energy = electronic energy + `0.719968994449 Ha` nuclear repulsion;
- HF as the classical baseline and exact diagonalization as the oracle.

## User Interaction

The user may retrieve the reference calculation, run VQE with a chosen initialization seed, inspect the optimized QCIS circuit and convergence trace, and compare HF, VQE and exact energies under the same energy convention.

## Acceptance Criterion

The absolute difference between VQE and exact electronic energies must not exceed `1.6 mHa`. Scientific tests must also enforce the variational lower bound, endianness, API schema and report consistency.

## Scope Boundary

The evidence is exact statevector simulation for one fixed instance. It supports workflow validation, not claims about quantum advantage, cloud execution or hardware performance.
