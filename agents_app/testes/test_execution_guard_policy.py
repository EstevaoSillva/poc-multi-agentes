import tempfile
import unittest
from pathlib import Path

from agents_app.policies.execution_guard import validate_candidate_paths


class TestExecutionGuardPolicy(unittest.TestCase):
    def test_validate_candidate_paths_allows_safe_relative_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            validate_candidate_paths(
                workspace_root=workspace,
                candidate_paths=["backend/main.py", "frontend/index.html"],
            )

    def test_validate_candidate_paths_blocks_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            with self.assertRaises(PermissionError):
                validate_candidate_paths(
                    workspace_root=workspace,
                    candidate_paths=["/etc/passwd"],
                )

    def test_validate_candidate_paths_blocks_directory_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            with self.assertRaises(PermissionError):
                validate_candidate_paths(
                    workspace_root=workspace,
                    candidate_paths=["../../outside.txt"],
                )

    def test_validate_candidate_paths_blocks_path_outside_allowed_scope(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            with self.assertRaises(PermissionError):
                validate_candidate_paths(
                    workspace_root=workspace,
                    candidate_paths=["backend/main.py", "frontend/index.html"],
                    allowed_paths=["backend/main.py"],
                )


if __name__ == "__main__":
    unittest.main()
