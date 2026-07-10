# VQE H2 Molecular Energy — Application Brief

## Goal
Build a TianYan quantum cloud showcase application that uses the Variational Quantum Eigensolver (VQE) to compute the ground-state energy of the H2 molecule. The quantum result must match or beat the classical baseline (exact diagonalization) within chemical accuracy (≤1.6 mHartree).

## User Workflow
1. User selects a bond distance for H2 (or uses the default equilibrium distance 0.735 Å).
2. System computes the H2 Hamiltonian at that bond distance.
3. Classical baseline: exact diagonalization of the Hamiltonian matrix → ground-state energy.
4. Quantum VQE: hardware-efficient ansatz + scipy optimizer on cqlib StatevectorSimulator → ground-state energy.
5. System displays both results and the energy error comparison.

## Inputs & Outputs
- **Input**: Bond distance (Å, float), optional ansatz layers (int, default=2)
- **Output**: Classical energy (Hartree), Quantum energy (Hartree), Energy error (mHartree), Convergence trace, Circuit diagram (QCIS)

## Task Type
Chemistry / Molecular simulation

## Data Status
Pre-computed H2 minimal basis (STO-3G) Hamiltonian coefficients from standard references. No external dataset needed.

## Baseline
Exact diagonalization of the 2-qubit Hamiltonian matrix using numpy.linalg.eigh. This gives the true ground-state energy for the given Hamiltonian.

## Primary Metric
- **Name**: energy_error (absolute deviation from exact ground-state energy in mHartree)
- **Direction**: lower_is_better
- **Threshold**: ≤1.6 mHartree (chemical accuracy)

## Quantum Route
VQE with hardware-efficient ansatz on cqlib StatevectorSimulator. Algorithm skill: cqlib-sdk + cqlib-vqe.

## Delivery Target
full_delivery: algorithm evidence + local FastAPI demo + qccp-web page + documentation

## Hardware Boundary
Simulator only (cqlib StatevectorSimulator). No real hardware execution in this delivery.

## Evidence Standard
Internal PoC / cloud showcase demo — reproducible, comparable, not publication-grade.

## Out of Scope
- Real hardware execution
- Larger molecules (LiH, H2O, etc.)
- Active space selection beyond minimal basis
- Error mitigation techniques
