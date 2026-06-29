"""Tests for deterministic quantum application artifact validation."""

from __future__ import annotations

import json
from pathlib import Path

from EvoScientist.tools.quantum_validation import (
    validate_quantum_application,
    validate_quantum_application_artifacts,
)


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def _report(*, value: float, metric: str = "accuracy", higher: bool = True) -> dict:
    return {
        "task": "classification",
        "data": {"dataset": "demo", "split": "80/20"},
        "primary_metric": metric,
        "higher_is_better": higher,
        "value": value,
        "command": "python run.py",
        "artifact_paths": ["artifacts/result.json"],
        "backend": "StatevectorSimulator",
        "limitations": ["smoke fixture"],
    }


def _complete_app(tmp_path: Path, *, baseline: float = 0.8, quantum: float = 0.9) -> Path:
    (tmp_path / "backend").mkdir()
    (tmp_path / "frontend" / "static").mkdir(parents=True)
    (tmp_path / "qccp" / "src" / "api").mkdir(parents=True)
    (tmp_path / "qccp" / "src" / "views" / "solution" / "vqlsSolver").mkdir(parents=True)

    _write_json(
        tmp_path / "requirements.json",
        {
            "task": "classification",
            "require_quantum_improvement": True,
            "require_packaging": True,
        },
    )
    _write_json(tmp_path / "baseline_report.json", _report(value=baseline))
    _write_json(tmp_path / "quantum_report.json", _report(value=quantum))
    (tmp_path / "backend" / "main.py").write_text(
        """
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@app.get("/")
def root():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post("/api/solve")
def solve(payload: dict):
    return {"solution": [1.0], "metric": 0.9}


@app.get("/api/params")
def params():
    return {"size": 2}


app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR / "static")), name="static")
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "frontend" / "index.html").write_text(
        """<link rel="stylesheet" href="/static/style.css"><script src="/static/app.js"></script>""",
        encoding="utf-8",
    )
    (tmp_path / "frontend" / "static" / "style.css").write_text("body{}", encoding="utf-8")
    (tmp_path / "frontend" / "static" / "app.js").write_text("console.log('ok')", encoding="utf-8")
    sfc = tmp_path / "qccp" / "src" / "views" / "solution" / "vqlsSolver" / "index.vue"
    sfc.write_text(
        """
<template>
  <section class="vqls-page">
    <el-button type="primary" @click="runSolve">{{ t('vqls.solve') }}</el-button>
    <div ref="chartRef" class="chart"></div>
  </section>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import * as echarts from 'echarts'

const { t } = useI18n()
const chartRef = ref(null)
let chartInstance

async function runSolve() {
  const response = await fetch('/api/solve', { method: 'POST' })
  return response.json()
}

async function renderChart() {
  await nextTick()
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  chartInstance.setOption({})
  chartInstance.resize()
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style lang="scss" scoped>
.vqls-page {
  color: #020814;
  background: #FFFFFF;
  border-radius: 8px;
  font-family: "Alibaba PuHuiTi 3.0", Arial, sans-serif;
}

.chart {
  height: 320px;
  background: #F4F7FC;
}
</style>
""".strip(),
        encoding="utf-8",
    )
    (tmp_path / "qccp" / "src" / "api" / "vqlsSolver.js").write_text(
        "export const solve = (request) => request({ url: '/solve', method: 'post' })\n",
        encoding="utf-8",
    )
    (tmp_path / "verification_report.md").write_text("verified /api/solve", encoding="utf-8")
    (tmp_path / "README.md").write_text("demo endpoint /api/solve", encoding="utf-8")
    (tmp_path / "INTEGRATE.md").write_text(
        "qccp route /solution/vqlsSolver uses /api/solve and /api/params",
        encoding="utf-8",
    )
    _write_json(
        tmp_path / "application_manifest.json",
        {
            "delivery_profile": "full_delivery",
            "algorithm": {
                "name": "Fixture VQLS",
                "task": "classification",
                "primary_metric": "accuracy",
            },
            "artifacts": {
                "requirements.json": "requirements.json",
                "solution_plan.md": "solution_plan.md",
                "baseline_report.json": "baseline_report.json",
                "quantum_report.json": "quantum_report.json",
                "verification_report.md": "verification_report.md",
                "README.md": "README.md",
                "INTEGRATE.md": "INTEGRATE.md",
            },
            "local_demo": {
                "backend_entrypoint": "backend/main.py",
                "app_symbol": "app",
                "entrypoint": "frontend/index.html",
                "endpoints": [
                    {
                        "path": "/api/solve",
                        "method": "POST",
                        "request_schema": {"type": "object"},
                        "response_schema": {"type": "object"},
                        "sample_request": {},
                        "errors": [{"status": 400, "message": "invalid request"}],
                    },
                    {
                        "path": "/api/params",
                        "method": "GET",
                        "request_schema": {"type": "object"},
                        "response_schema": {"type": "object"},
                        "errors": [{"status": 500, "message": "service error"}],
                    },
                ],
                "static_assets": [
                    {"url": "/static/style.css", "path": "frontend/static/style.css"},
                    {"url": "/static/app.js", "path": "frontend/static/app.js"},
                ],
            },
            "qccp_web": {
                "pageKey": "vqlsSolver",
                "route": "/solution/vqlsSolver",
                "sfc": "qccp/src/views/solution/vqlsSolver/index.vue",
                "api_module": "qccp/src/api/vqlsSolver.js",
                "api_paths": ["/api/solve"],
                "verification_command": "npm run build",
            },
            "docs": {"files": ["README.md", "INTEGRATE.md", "verification_report.md"]},
            "verification": {"commands": ["python -m pytest"]},
            "limitations": ["fixture only"],
        },
    )
    (tmp_path / "solution_plan.md").write_text("plan", encoding="utf-8")
    return tmp_path


def test_missing_artifacts_block(tmp_path):
    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert "baseline_report.json" in result["missing_artifacts"]
    assert any("missing artifacts" in blocker for blocker in result["blockers"])


def test_schema_missing_fields_block(tmp_path):
    _write_json(tmp_path / "requirements.json", {})
    _write_json(tmp_path / "baseline_report.json", {"value": 0.8})
    _write_json(tmp_path / "quantum_report.json", _report(value=0.9))
    (tmp_path / "verification_report.md").write_text("verified", encoding="utf-8")

    result = validate_quantum_application_artifacts(
        str(tmp_path),
        require_packaging=False,
    )

    assert result["status"] == "blocked"
    assert any("baseline_report" in blocker for blocker in result["blockers"])


def test_metric_mismatch_blocks_comparison(tmp_path):
    _complete_app(tmp_path)
    _write_json(tmp_path / "quantum_report.json", _report(value=0.9, metric="f1"))

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["metric_comparison"]["comparable"] is False
    assert result["metric_comparison"]["mismatched_fields"] == ["primary_metric"]
    assert result["status"] == "blocked"


def test_quantum_must_beat_baseline_by_default(tmp_path):
    _complete_app(tmp_path, baseline=0.9, quantum=0.85)

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["metric_comparison"]["comparable"] is True
    assert result["metric_comparison"]["quantum_improved"] is False
    assert result["status"] == "blocked"


def test_packaging_evidence_required_when_enabled(tmp_path):
    _complete_app(tmp_path)
    (tmp_path / "INTEGRATE.md").unlink()
    (tmp_path / "README.md").unlink()

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert "README.md" in result["missing_artifacts"]
    assert "INTEGRATE.md" in result["missing_artifacts"]


def test_complete_application_passes_and_tool_returns_json(tmp_path):
    _complete_app(tmp_path)

    result = validate_quantum_application_artifacts(str(tmp_path))
    tool_result = json.loads(
        validate_quantum_application.invoke({"app_dir": str(tmp_path)})
    )

    assert result["status"] == "passed"
    assert result["delivery_profile"] == "full_delivery"
    assert result["validation_layers"] == ["algorithm", "local_demo", "qccp_web", "docs"]
    assert result["metric_comparison"]["quantum_improved"] is True
    assert tool_result["status"] == "passed"
    assert result["application_manifest"]["present"] is True


def test_algorithm_only_profile_does_not_require_frontend_or_backend(tmp_path):
    _write_json(
        tmp_path / "requirements.json",
        {
            "task": "classification",
            "require_quantum_improvement": True,
        },
    )
    _write_json(tmp_path / "baseline_report.json", _report(value=0.8))
    _write_json(tmp_path / "quantum_report.json", _report(value=0.9))
    (tmp_path / "verification_report.md").write_text("verified", encoding="utf-8")
    _write_json(
        tmp_path / "application_manifest.json",
        {
            "delivery_profile": "algorithm_only",
            "algorithm": {
                "name": "Algorithm Only",
                "task": "classification",
                "primary_metric": "accuracy",
            },
            "artifacts": {
                "requirements.json": "requirements.json",
                "baseline_report.json": "baseline_report.json",
                "quantum_report.json": "quantum_report.json",
                "verification_report.md": "verification_report.md",
            },
            "verification": {"commands": ["python run.py"]},
            "limitations": ["algorithm only"],
        },
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "passed"
    assert result["validation_layers"] == ["algorithm"]


def test_local_fastapi_demo_profile_catches_static_mount_404(tmp_path):
    _complete_app(tmp_path)
    manifest_path = tmp_path / "application_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["delivery_profile"] = "local_fastapi_demo"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    backend = tmp_path / "backend" / "main.py"
    backend.write_text(
        backend.read_text(encoding="utf-8").replace(
            'StaticFiles(directory=str(FRONTEND_DIR / "static"))',
            "StaticFiles(directory=str(FRONTEND_DIR))",
        ),
        encoding="utf-8",
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert result["validation_layers"] == ["algorithm", "local_demo"]
    assert any("[local_demo]" in blocker and "/static/style.css:404" in blocker for blocker in result["blockers"])


def test_local_fastapi_demo_profile_blocks_cdn_dependencies(tmp_path):
    _complete_app(tmp_path)
    manifest_path = tmp_path / "application_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["delivery_profile"] = "local_fastapi_demo"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    index = tmp_path / "frontend" / "index.html"
    index.write_text(
        index.read_text(encoding="utf-8") + '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
        encoding="utf-8",
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("[local_demo]" in blocker and "external_resource" in blocker for blocker in result["blockers"])


def test_qccp_web_page_profile_blocks_missing_i18n(tmp_path):
    _complete_app(tmp_path)
    manifest_path = tmp_path / "application_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["delivery_profile"] = "qccp_web_page"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    sfc = tmp_path / "qccp" / "src" / "views" / "solution" / "vqlsSolver" / "index.vue"
    sfc.write_text(sfc.read_text(encoding="utf-8").replace("useI18n", "useLocale"), encoding="utf-8")

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert result["validation_layers"] == ["algorithm", "qccp_web"]
    assert any("[qccp_web]" in blocker and "qccp_web.sfc:i18n" in blocker for blocker in result["blockers"])


def test_requirements_can_disable_quantum_improvement_for_feasibility(tmp_path):
    _complete_app(tmp_path, baseline=0.9, quantum=0.85)
    _write_json(
        tmp_path / "requirements.json",
        {
            "task": "feasibility",
            "require_quantum_improvement": False,
            "require_packaging": True,
        },
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["metric_comparison"]["quantum_improved"] is False
    assert result["status"] == "passed"


def test_requirements_can_disable_packaging_contract_for_feasibility(tmp_path):
    _write_json(
        tmp_path / "requirements.json",
        {
            "task": "feasibility",
            "require_quantum_improvement": True,
            "require_packaging": False,
        },
    )
    _write_json(tmp_path / "baseline_report.json", _report(value=0.8))
    _write_json(tmp_path / "quantum_report.json", _report(value=0.9))
    (tmp_path / "verification_report.md").write_text("verified", encoding="utf-8")
    _write_json(
        tmp_path / "application_manifest.json",
        {
            "delivery_profile": "algorithm_only",
            "algorithm": {
                "name": "Feasibility",
                "task": "classification",
                "primary_metric": "accuracy",
            },
            "artifacts": {
                "requirements.json": "requirements.json",
                "baseline_report.json": "baseline_report.json",
                "quantum_report.json": "quantum_report.json",
                "verification_report.md": "verification_report.md",
            },
            "verification": {"commands": ["python run.py"]},
            "limitations": ["no packaging requested"],
        },
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "passed"
    assert result["delivery_profile"] == "algorithm_only"
    assert result["validation_layers"] == ["algorithm"]


def test_manifest_api_path_drift_blocks_qccp_frontend(tmp_path):
    _complete_app(tmp_path)
    sfc = tmp_path / "qccp" / "src" / "views" / "solution" / "vqlsSolver" / "index.vue"
    sfc.write_text(sfc.read_text(encoding="utf-8").replace("/api/solve", "/api/vqls/solve"), encoding="utf-8")

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("/api/vqls/solve" in blocker for blocker in result["blockers"])


def test_backend_contract_route_mismatch_blocks(tmp_path):
    _complete_app(tmp_path)
    backend = tmp_path / "backend" / "main.py"
    backend.write_text(backend.read_text(encoding="utf-8").replace("/api/solve", "/api/run"), encoding="utf-8")

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("backend contract" in blocker and "/api/solve" in blocker for blocker in result["blockers"])


def test_static_asset_reference_mismatch_blocks(tmp_path):
    _complete_app(tmp_path)
    index = tmp_path / "frontend" / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace("/static/style.css", "/static/missing.css"), encoding="utf-8")

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("static asset" in blocker and "/static/missing.css" in blocker for blocker in result["blockers"])


def test_qccp_ui_token_violation_blocks(tmp_path):
    _complete_app(tmp_path)
    sfc = tmp_path / "qccp" / "src" / "views" / "solution" / "vqlsSolver" / "index.vue"
    sfc.write_text(
        sfc.read_text(encoding="utf-8").replace("#FFFFFF", "#123456").replace("border-radius: 8px", "border-radius: 16px"),
        encoding="utf-8",
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("qccp UI" in blocker and "#123456" in blocker for blocker in result["blockers"])


def test_documented_endpoint_drift_blocks(tmp_path):
    _complete_app(tmp_path)
    (tmp_path / "INTEGRATE.md").write_text(
        "qccp route /solution/vqlsSolver uses /api/vqls/solve",
        encoding="utf-8",
    )

    result = validate_quantum_application_artifacts(str(tmp_path))

    assert result["status"] == "blocked"
    assert any("documentation" in blocker and "/api/vqls/solve" in blocker for blocker in result["blockers"])
