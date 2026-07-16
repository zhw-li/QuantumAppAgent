"""Typed results for deterministic scientific validation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

CheckStatus = Literal["passed", "failed", "inconclusive"]
ScientificStatus = Literal["passed", "failed", "inconclusive", "manual_review"]


@dataclass(frozen=True)
class ScientificCheck:
    """One independently evaluated scientific invariant or oracle."""

    name: str
    status: CheckStatus
    code: str
    message: str
    expected: Any = None
    actual: Any = None
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def passed(name: str, code: str, message: str, **evidence: Any) -> ScientificCheck:
    return ScientificCheck(
        name=name,
        status="passed",
        code=code,
        message=message,
        evidence=evidence,
    )


def failed(
    name: str,
    code: str,
    message: str,
    *,
    expected: Any = None,
    actual: Any = None,
    **evidence: Any,
) -> ScientificCheck:
    return ScientificCheck(
        name=name,
        status="failed",
        code=code,
        message=message,
        expected=expected,
        actual=actual,
        evidence=evidence,
    )


def inconclusive(
    name: str, code: str, message: str, **evidence: Any
) -> ScientificCheck:
    return ScientificCheck(
        name=name,
        status="inconclusive",
        code=code,
        message=message,
        evidence=evidence,
    )


def aggregate_status(checks: list[ScientificCheck]) -> ScientificStatus:
    if any(check.status == "failed" for check in checks):
        return "failed"
    if any(check.status == "inconclusive" for check in checks):
        return "inconclusive"
    return "passed"
