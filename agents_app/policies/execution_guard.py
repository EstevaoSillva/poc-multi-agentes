"""Deterministic execution guard rules for filesystem operations."""

from pathlib import Path


def validate_candidate_paths(
    *,
    workspace_root: Path,
    candidate_paths: list[str],
    allowed_paths: list[str] | None = None,
) -> None:
    root = workspace_root.resolve()
    allowed_set = set(allowed_paths or [])

    for candidate in candidate_paths:
        candidate_path = Path(candidate)
        if candidate_path.is_absolute() or ".." in candidate_path.parts:
            raise PermissionError(f"Unsafe path detected: {candidate}")

        target = (workspace_root / candidate).resolve()
        if not str(target).startswith(str(root)):
            raise PermissionError(f"Path outside workspace: {candidate}")

        if allowed_set and candidate not in allowed_set:
            raise PermissionError(f"Path outside approved scope: {candidate}")
