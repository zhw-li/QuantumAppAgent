"""Text checks for EvoScientist skills (built-in and workspace).

Skills can live in two tiers: the built-in layer shipped in the wheel
(`EvoScientist/skills/`) and the optional workspace layer (`./skills/`). These
tests look up each skill across both tiers. In a clean checkout where the
optional workspace skills are absent, the tests that only need workspace skills
skip instead of failing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
# Built-in layer: ships inside the package (EvoScientist/skills/).
BUILTIN_SKILLS_DIR = ROOT / "EvoScientist" / "skills"
# Workspace layer: optional, gitignored local skills (./skills/).
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
    "qccp-ui",
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


def _require_any_skills_layer() -> None:
    """Skip unless at least one skills tier is present."""
    if not (BUILTIN_SKILLS_DIR.exists() or SKILLS_DIR.exists()):
        pytest.skip("no skills directory is present")


def _skill_path(name: str) -> Path:
    """Resolve a skill directory across built-in then workspace tiers."""
    for base in (BUILTIN_SKILLS_DIR, SKILLS_DIR):
        candidate = base / name
        if (candidate / "SKILL.md").is_file():
            return candidate
    raise AssertionError(f"missing skill: {name}")


def _read_skill(name: str) -> str:
    return (_skill_path(name) / "SKILL.md").read_text(encoding="utf-8")


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
    ep_dir = _skill_path("experiment-pipeline")
    stage_log = (ep_dir / "assets" / "stage-log-template.md").read_text(
        encoding="utf-8"
    )
    tracker = (ep_dir / "assets" / "pipeline-tracker-template.md").read_text(
        encoding="utf-8"
    )

    assert "Skill Used" in text
    assert "Skill Used" in stage_log
    assert "Skill Used" in tracker


def test_skills_do_not_reintroduce_release_gate_system():
    _require_any_skills_layer()
    checked_paths = [
        _skill_path(name) / "SKILL.md"
        for name in NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS
    ]
    ep_dir = _skill_path("experiment-pipeline")
    checked_paths.extend(
        [
            ep_dir / "assets" / "stage-log-template.md",
            ep_dir / "assets" / "pipeline-tracker-template.md",
        ]
    )
    text = "\n".join(path.read_text(encoding="utf-8") for path in checked_paths)

    for term in OLD_GATE_TERMS:
        assert term not in text
