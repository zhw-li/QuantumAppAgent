# Validation Plan: H2 VQE

## Scientific Gates

- The 4x4 Hamiltonian is Hermitian and has exact electronic ground energy `-1.857275030202 Ha`.
- The nuclear-repulsion term is `0.719968994449 Ha`; every total energy equals electronic energy plus this constant.
- The HF determinant is `|01>` in the `|q1 q0>` convention and its error is `20.307038999 mHa`.
- Cqlib expectation values match an independent dense-matrix calculation.
- Every reported VQE result respects the variational lower bound and has absolute error at most `1.6 mHa`.

## Engineering Gates

- `/api/info`, `/api/baseline`, `/api/vqe` and `/api/compare` return self-describing, mutually consistent fields.
- Standalone and QCCP pages consume the nested API schema and distinguish electronic from total energy.
- Baseline and quantum reports use the same task, instance and primary metric.

## Commands

```bash
python -m algorithms.baseline
python -m algorithms.vqe
python -m pytest tests/test_vqe_h2.py -q
python -m app.main --check
```

## Claim Gate

The application may state that VQE reaches chemical accuracy for this fixed exact-statevector instance. It may not infer quantum advantage, noisy-device performance or transfer to larger molecular systems.
