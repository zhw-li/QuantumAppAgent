"""Text checks for workspace EvoScientist skills.

These tests intentionally inspect the local workspace `skills/` layer. In a
clean checkout where the optional workspace skills are absent, they skip instead
of making the package test suite depend on ignored local files.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

NATIVE_QUANTUM_SKILLS = [
    "academic-slides",
    "evo-memory",
    "experiment-craft",
    "experiment-iterative-coder",
    "experiment-pipeline",
    "nano-banana",
    "paper-navigator",
    "paper-planning",
    "paper-rebuttal",
    "paper-review",
    "paper-writing",
    "research-ideation",
    "research-survey",
]

CQ_QCCP_SKILLS = [
    "cqlib-hybrid",
    "cqlib-qaoa",
    "cqlib-qml",
    "cqlib-sdk",
    "cqlib-vqe",
    "qccp-frontend",
    "qccp-service",
    "ui-design-spec",
]

QUANTUM_TRIGGER_TERMS = (
    "quantum",
    "cqlib",
    "qccp",
    "cloud showcase",
    "application",
    "poc",
)

OLD_GATE_TERMS = (
    "G0-G5",
    "G0_REQUIREMENT_STRUCTURED",
    "release_gate.json",
    "quantum-app-validation",
    "quantum-app-delivery",
)


def _require_workspace_skills() -> None:
    if not SKILLS_DIR.exists():
        pytest.skip("workspace skills directory is not present")


def _read_skill(name: str) -> str:
    _require_workspace_skills()
    path = SKILLS_DIR / name / "SKILL.md"
    assert path.exists(), f"missing skill: {name}"
    return path.read_text(encoding="utf-8")


def _frontmatter(text: str) -> str:
    match = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    assert match, "missing YAML frontmatter"
    return match.group(1)


def _description(text: str) -> str:
    frontmatter = _frontmatter(text)
    match = re.search(r'^description:\s*"(.*)"\s*$', frontmatter, re.MULTILINE)
    assert match, "missing quoted description"
    return match.group(1)


@pytest.mark.parametrize("name", NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS)
def test_skill_descriptions_include_quantum_application_triggers(name: str):
    description = _description(_read_skill(name)).lower()
    assert any(term in description for term in QUANTUM_TRIGGER_TERMS), name
    assert any(
        cue in description
        for cue in ("guides", "use when", "trigger", "do not use")
    ), name


@pytest.mark.parametrize("name", NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS)
def test_skills_define_use_and_non_use_boundaries(name: str):
    text = _read_skill(name).lower()
    assert "when to use" in text, name
    assert ("when not to use" in text) or ("do not use for" in text), name


@pytest.mark.parametrize("name", CQ_QCCP_SKILLS)
def test_cqlib_qccp_skills_follow_native_frontmatter_shape(name: str):
    frontmatter = _frontmatter(_read_skill(name)).lower()
    assert "name:" in frontmatter
    assert "description:" in frontmatter
    assert "allowed-tools:" in frontmatter
    assert "metadata:" in frontmatter


@pytest.mark.parametrize("name", CQ_QCCP_SKILLS)
def test_cqlib_qccp_skills_contribute_evidence_not_final_readiness(name: str):
    text = _read_skill(name).lower()
    assert "experiment-pipeline" in text, name
    assert "evidence" in text, name
    assert "final delivery readiness" in text or "do not decide delivery readiness" in text


def test_experiment_pipeline_logs_actual_skill_usage():
    text = _read_skill("experiment-pipeline")
    stage_log = (SKILLS_DIR / "experiment-pipeline" / "assets" / "stage-log-template.md").read_text(
        encoding="utf-8"
    )
    tracker = (
        SKILLS_DIR / "experiment-pipeline" / "assets" / "pipeline-tracker-template.md"
    ).read_text(encoding="utf-8")

    assert "Skill Used" in text
    assert "Skill Used" in stage_log
    assert "Skill Used" in tracker


def test_workspace_skills_do_not_reintroduce_release_gate_system():
    _require_workspace_skills()
    checked_paths = [
        SKILLS_DIR / name / "SKILL.md"
        for name in NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS
    ]
    checked_paths.extend(
        [
            SKILLS_DIR / "experiment-pipeline" / "assets" / "stage-log-template.md",
            SKILLS_DIR / "experiment-pipeline" / "assets" / "pipeline-tracker-template.md",
        ]
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

    for term in OLD_GATE_TERMS:
        assert term not in text
