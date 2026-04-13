"""Typed contracts and normalization helpers for agent responses."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FileContent:
    path: str
    content: str


@dataclass(frozen=True)
class GenerationResult:
    status: str
    files: list[FileContent]
    notes: str = ""


@dataclass(frozen=True)
class ValidationCheck:
    check: str
    result: str
    details: str = ""


@dataclass(frozen=True)
class ValidationResult:
    status: str
    step: int | None
    checks: list[ValidationCheck]


@dataclass(frozen=True)
class EditResult:
    status: str
    files: list[FileContent]
    notes: str = ""


@dataclass(frozen=True)
class IntentDecision:
    intent: str
    confidence: float
    reason: str = ""


@dataclass(frozen=True)
class PlanDecision:
    strategy: str
    tools: list[dict[str, Any]]
    description: str = ""


def _normalize_status(raw: str, *, mapping: dict[str, str], default: str) -> str:
    key = str(raw or "").strip().lower()
    return mapping.get(key, default)


def _parse_files(payload: dict[str, Any], *, field_name: str = "files") -> list[FileContent]:
    files = payload.get(field_name, [])
    if not isinstance(files, list):
        raise ValueError(f"'{field_name}' must be a list")

    parsed: list[FileContent] = []
    for item in files:
        if not isinstance(item, dict):
            raise ValueError(f"Invalid file item in '{field_name}'")
        path = item.get("path")
        content = item.get("content")
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Invalid file path")
        if not isinstance(content, str):
            raise ValueError(f"Invalid content for file '{path}'")
        parsed.append(FileContent(path=path, content=content))
    return parsed


def parse_generation_result(payload: dict[str, Any]) -> GenerationResult:
    if not isinstance(payload, dict):
        raise ValueError("Generation payload must be a JSON object")
    status = _normalize_status(
        payload.get("status"),
        mapping={"success": "success", "needs_fix": "needs_fix"},
        default="needs_fix",
    )
    files = _parse_files(payload, field_name="files")
    notes = payload.get("notes", "")
    return GenerationResult(status=status, files=files, notes=str(notes or ""))


def parse_validation_result(payload: dict[str, Any]) -> ValidationResult:
    if not isinstance(payload, dict):
        raise ValueError("Validation payload must be a JSON object")
    status = _normalize_status(
        payload.get("status"),
        mapping={"passed": "passed", "pass": "passed", "failed": "failed", "fail": "failed"},
        default="failed",
    )
    checks_raw = payload.get("checks", [])
    checks: list[ValidationCheck] = []
    if isinstance(checks_raw, list):
        for item in checks_raw:
            if not isinstance(item, dict):
                continue
            checks.append(
                ValidationCheck(
                    check=str(item.get("check", "")),
                    result=_normalize_status(
                        item.get("result"),
                        mapping={"pass": "pass", "passed": "pass", "fail": "fail", "failed": "fail"},
                        default="fail",
                    ),
                    details=str(item.get("details", "")),
                )
            )
    step = payload.get("step")
    return ValidationResult(status=status, step=step if isinstance(step, int) else None, checks=checks)


def parse_edit_result(payload: dict[str, Any]) -> EditResult:
    if not isinstance(payload, dict):
        raise ValueError("Edit payload must be a JSON object")
    status = _normalize_status(
        payload.get("status"),
        mapping={"success": "success", "blocked": "blocked"},
        default="blocked",
    )
    files_field = "files" if "files" in payload else "changes"
    files = _parse_files(payload, field_name=files_field)
    notes = payload.get("notes", "")
    return EditResult(status=status, files=files, notes=str(notes or ""))


def parse_intent_decision(payload: dict[str, Any]) -> IntentDecision:
    if not isinstance(payload, dict):
        raise ValueError("Intent payload must be a JSON object")
    intent = str(payload.get("intent", "unknown")).strip().lower() or "unknown"
    confidence_raw = payload.get("confidence", 0.0)
    try:
        confidence = float(confidence_raw)
    except Exception as exc:  # pragma: no cover
        raise ValueError("Invalid confidence in intent payload") from exc
    reason = str(payload.get("reason", ""))
    return IntentDecision(intent=intent, confidence=confidence, reason=reason)


def parse_plan_decision(payload: dict[str, Any]) -> PlanDecision:
    if not isinstance(payload, dict):
        raise ValueError("Plan payload must be a JSON object")
    strategy = _normalize_status(
        payload.get("strategy"),
        mapping={"chat_only": "chat_only", "execute_tools": "execute_tools"},
        default="chat_only",
    )
    tools_raw = payload.get("tools", [])
    tools = tools_raw if isinstance(tools_raw, list) else []
    normalized_tools: list[dict[str, Any]] = []
    for item in tools:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if not isinstance(name, str) or not name:
            continue
        args = item.get("args", {})
        normalized_tools.append({
            "name": name,
            "args": args if isinstance(args, dict) else {},
        })
    description = str(payload.get("description", ""))
    return PlanDecision(strategy=strategy, tools=normalized_tools, description=description)
