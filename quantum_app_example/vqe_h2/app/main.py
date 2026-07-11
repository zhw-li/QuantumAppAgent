"""FastAPI backend for the validated H2 VQE reference application."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from algorithms.baseline import compute_reference
from algorithms.hamiltonian import BOND_DISTANCE_ANGSTROM, HF_BITSTRING, N_QUBITS
from algorithms.vqe import OPTIMIZER, build_ansatz, run_vqe

app = FastAPI(title="H2 Ground-State Energy with VQE", version="2.0.0")


def _reference_payload() -> dict[str, float | str]:
    reference = compute_reference()
    return {
        "hf_bitstring": HF_BITSTRING,
        "bitstring_convention": "|q1 q0>; qubit 0 is the least-significant bit",
        "hf_electronic_energy_hartree": round(
            reference.hf_electronic_energy_hartree, 12
        ),
        "hf_total_energy_hartree": round(reference.hf_total_energy_hartree, 12),
        "exact_electronic_energy_hartree": round(
            reference.exact_electronic_energy_hartree, 12
        ),
        "exact_total_energy_hartree": round(
            reference.exact_total_energy_hartree, 12
        ),
        "nuclear_repulsion_energy_hartree": round(
            reference.nuclear_repulsion_energy_hartree, 12
        ),
        "hf_error_mhartree": round(reference.hf_error_mhartree, 9),
    }


def _vqe_payload(seed: int) -> dict[str, object]:
    result = run_vqe(seed)
    reference = compute_reference()
    circuit, _ = build_ansatz()
    bound_circuit = circuit.assign_parameters(result.optimal_parameters)
    return {
        "seed": seed,
        "initial_theta": result.initial_theta,
        "optimal_theta": result.optimal_theta,
        "electronic_energy_hartree": round(result.electronic_energy_hartree, 12),
        "total_energy_hartree": round(result.total_energy_hartree, 12),
        "energy_error_mhartree": round(result.energy_error_mhartree, 9),
        "correlation_energy_recovered_percent": round(
            result.correlation_energy_recovered_percent, 9
        ),
        "parameters": 1,
        "circuit_depth": circuit.depth(),
        "evaluations": result.evaluations,
        "optimizer_success": result.optimizer_success,
        "optimizer_message": result.optimizer_message,
        "qcis": bound_circuit.qcis,
        "convergence": [
            {
                "evaluation": evaluation,
                "electronic_energy_hartree": round(electronic_energy, 12),
                "total_energy_hartree": round(
                    electronic_energy + reference.nuclear_repulsion_energy_hartree,
                    12,
                ),
            }
            for evaluation, electronic_energy in result.convergence
        ],
    }


@app.get("/api/info")
async def api_info():
    """Return the fixed scientific and execution configuration."""
    return {
        "name": "H2 Ground-State Energy with VQE",
        "molecule": "H2",
        "basis": "STO-3G",
        "bond_distance_angstrom": BOND_DISTANCE_ANGSTROM,
        "qubits": N_QUBITS,
        "ansatz": "particle_conserving_h2_subspace",
        "parameters": 1,
        "optimizer": OPTIMIZER,
        "backend": "cqlib.StatevectorSimulator",
        "energy_convention": "electronic_plus_nuclear_repulsion",
        "evidence_scope": "exact statevector simulation of one fixed H2 instance",
    }


@app.get("/api/baseline")
async def api_baseline():
    """Return Hartree--Fock and exact-diagonalization references."""
    try:
        return _reference_payload()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/api/vqe")
async def api_vqe(
    seed: int = Query(
        default=42,
        ge=0,
        le=2**32 - 1,
        description="Seed controlling the random initial variational angle",
    ),
):
    """Run one reproducible VQE optimization."""
    try:
        return _vqe_payload(seed)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/api/compare")
async def api_compare():
    """Return like-for-like HF, exact and VQE results for seed 42."""
    try:
        baseline = _reference_payload()
        vqe = _vqe_payload(42)
        return {
            "baseline": baseline,
            "vqe": vqe,
            "correlation_energy_recovered_percent": vqe[
                "correlation_energy_recovered_percent"
            ],
            "comparison_scope": (
                "All energies use the same fixed two-qubit H2 Hamiltonian and "
                "the same nuclear-repulsion constant."
            ),
        }
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})


@app.get("/health")
async def health():
    return {"status": "ok"}


_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="H2 VQE FastAPI server")
    parser.add_argument(
        "--check", action="store_true", help="Verify that the application imports"
    )
    args = parser.parse_args()

    if args.check:
        print("Import check passed: FastAPI application created successfully")
    else:
        import uvicorn

        uvicorn.run(
            app,
            host=os.getenv("APP_BIND_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_BIND_PORT", "8080")),
        )
