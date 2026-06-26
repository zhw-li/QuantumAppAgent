"""Text checks for EvoScientist built-in skills.

The workspace layer (`./skills/`) is intentionally gitignored and may override
or extend skills at runtime, but it is not a release baseline. Required skills
must live in `EvoScientist/skills/` so clean checkouts and packaged wheels do
not depend on local ignored files.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
# Built-in layer: ships inside the package (EvoScientist/skills/).
BUILTIN_SKILLS_DIR = ROOT / "EvoScientist" / "skills"

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


def _skill_path(name: str) -> Path:
    """Resolve a required built-in skill directory."""
    candidate = BUILTIN_SKILLS_DIR / name
    if (candidate / "SKILL.md").is_file():
        return candidate
    raise AssertionError(f"missing skill: {name}")


def _read_skill(name: str) -> str:
    return (_skill_path(name) / "SKILL.md").read_text(encoding="utf-8")


def _builtin_skill_names() -> set[str]:
    return {
        path.parent.name
        for path in BUILTIN_SKILLS_DIR.glob("*/SKILL.md")
        if path.is_file()
    }


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


def test_required_skills_are_packaged_as_builtins():
    required = set(NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS)
    assert required <= _builtin_skill_names()


def test_prompt_referenced_core_skills_exist_in_builtin_layer():
    from EvoScientist.prompts import get_system_prompt

    text = get_system_prompt()
    referenced = set(re.findall(r"`([a-z][a-z0-9-]+)`", text))
    skill_like = {
        name
        for name in referenced
        if name in set(NATIVE_QUANTUM_SKILLS + CQ_QCCP_SKILLS)
    }
    assert skill_like <= _builtin_skill_names()
