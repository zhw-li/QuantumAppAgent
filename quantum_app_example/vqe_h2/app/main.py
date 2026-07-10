"""FastAPI backend for VQE H2 Molecular Energy application.

Single-origin server: serves static frontend at / and API under /api on port 8080.
"""

import os
import sys

# Allow importing algorithms from the parent package
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from algorithms.baseline import compute_hf_energy, run_baseline
from algorithms.vqe import build_ansatz, run_vqe

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="VQE H2 Molecular Energy", version="1.0.0")

# ---------------------------------------------------------------------------
# API endpoints (all query-params, no path params)
# ---------------------------------------------------------------------------


@app.get("/api/info")
async def api_info():
    """Return application metadata."""
    return {
        "name": "VQE H2 Molecular Energy",
        "molecule": "H2",
        "basis": "STO-3G",
        "bond_distance_angstrom": 0.735,
        "qubits": 2,
        "ansatz": "hardware_efficient",
        "default_layers": 2,
        "optimizer": "COBYLA",
        "backend": "cqlib.StatevectorSimulator",
    }


@app.get("/api/baseline")
async def api_baseline():
    """Run exact diagonalization and return baseline results."""
    try:
        exact_energy = run_baseline()
        hf_energy = compute_hf_energy()
        hf_error_mhartree = (hf_energy - exact_energy) * 1000
        return {
            "hf_energy_hartree": round(hf_energy, 10),
            "exact_energy_hartree": round(exact_energy, 10),
            "hf_error_mhartree": round(hf_error_mhartree, 6),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/vqe")
async def api_vqe(
    seed: int = Query(default=42, description="Random seed for optimization"),
    layers: int = Query(default=2, description="Number of ansatz layers"),
):
    """Run VQE with the given seed and layers, return quantum results."""
    try:
        energy, convergence = run_vqe(seed=seed, layers=layers)
        exact_energy = run_baseline()
        error_mhartree = (energy - exact_energy) * 1000

        # Build circuit and bind optimal parameters for QCIS output
        circuit, param_names = build_ansatz(layers=layers)
        from scipy.optimize import minimize
        import numpy as np

        np.random.seed(seed)
        initial_params = np.zeros(len(param_names))

        # Re-run optimization to get final params
        # We already have convergence from run_vqe; re-optimise to get params
        from algorithms.hamiltonian import H2_HAMILTONIAN
        from algorithms.vqe import compute_energy

        def _cost(params):
            pd = dict(zip(param_names, params))
            return compute_energy(circuit, pd, H2_HAMILTONIAN)

        result = minimize(
            _cost,
            initial_params,
            method="COBYLA",
            options={"maxiter": 500, "tol": 1e-6},
        )
        final_params = result.x
        param_dict = dict(zip(param_names, final_params))
        bound_circuit = circuit.assign_parameters(param_dict)
        qcis_str = bound_circuit.qcis

        circuit_depth = circuit.depth()

        # Format convergence trace as list of {iteration, energy}
        conv_trace = [{"iteration": it, "energy": round(e, 10)} for it, e in convergence]

        return {
            "energy_hartree": round(energy, 10),
            "exact_energy_hartree": round(exact_energy, 10),
            "energy_error_mhartree": round(error_mhartree, 6),
            "circuit_depth": circuit_depth,
            "qcis": qcis_str,
            "convergence": conv_trace,
            "seed": seed,
            "layers": layers,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/compare")
async def api_compare():
    """Return both baseline and VQE results for side-by-side comparison."""
    try:
        # Baseline
        exact_energy = run_baseline()
        hf_energy = compute_hf_energy()
        hf_error_mhartree = (hf_energy - exact_energy) * 1000

        # VQE with default seed=42, layers=2
        vqe_energy, convergence = run_vqe(seed=42, layers=2)
        vqe_error_mhartree = (vqe_energy - exact_energy) * 1000

        circuit, _ = build_ansatz(layers=2)
        circuit_depth = circuit.depth()

        return {
            "baseline": {
                "method": "Hartree-Fock",
                "energy_hartree": round(hf_energy, 10),
                "exact_energy_hartree": round(exact_energy, 10),
                "error_mhartree": round(hf_error_mhartree, 6),
            },
            "vqe": {
                "method": "VQE (hardware_efficient, 2 layers, COBYLA)",
                "energy_hartree": round(vqe_energy, 10),
                "exact_energy_hartree": round(exact_energy, 10),
                "error_mhartree": round(vqe_error_mhartree, 6),
                "circuit_depth": circuit_depth,
            },
            "improvement_mhartree": round(hf_error_mhartree - vqe_error_mhartree, 6),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Static frontend (must be last — catches all remaining routes)
# ---------------------------------------------------------------------------

_static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=_static_dir, html=True), name="static")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="VQE H2 FastAPI server")
    parser.add_argument("--check", action="store_true", help="Verify server can start (import check)")
    args = parser.parse_args()

    if args.check:
        print("Import check passed — FastAPI app created successfully")
    else:
        import uvicorn

        uvicorn.run(
            app,
            host=os.getenv("APP_BIND_HOST", "0.0.0.0"),
            port=int(os.getenv("APP_BIND_PORT", "8080")),
        )
