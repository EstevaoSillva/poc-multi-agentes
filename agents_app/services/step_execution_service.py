from pathlib import Path
from typing import Dict, List

from agents_app.agents.core.execution_guard import execution_guard_agent
from agents_app.agents.generator_agent import generator_agent
from agents_app.agents.actions.test_agent import test_agent
from agents_app.agents.actions import editor_agent
from agents_app.contracts import (
    parse_edit_result,
    parse_generation_result,
    parse_validation_result,
)
from agents_app.policies.execution_guard import validate_candidate_paths
from agents_app.state.project_state_repository import ProjectStateRepository
from agents_app.utils import extract_text_from_run, safe_json_parse


class StepExecutionService:
    def __init__(self, workspace: Path, state_repo: ProjectStateRepository):
        self.workspace = workspace
        self.state_repo = state_repo

    # -------------------------
    # Helpers
    # -------------------------

    def _existing_files(self) -> List[str]:
        if not self.workspace.exists():
            return []

        return [
            str(p.relative_to(self.workspace))
            for p in self.workspace.rglob("*")
            if p.is_file()
        ]

    def _next_step(self, execution_plan: List[Dict]) -> Dict | None:
        state = self.state_repo.get_state()
        completed = set(state["completed_steps"])

        for step in execution_plan:
            if step["step"] not in completed:
                return step

        return None

    def _write_files(self, files: List[Dict]):
        for file in files:
            path = self.workspace / file["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(file["content"], encoding="utf-8")

    def _guard_generated_files(self, *, step: Dict, generated_paths: List[str]) -> None:
        allowed = list(step.get("outputs", []))
        validate_candidate_paths(
            workspace_root=self.workspace,
            candidate_paths=generated_paths,
            allowed_paths=allowed,
        )

        # Advisory LLM guard after deterministic checks.
        try:
            raw = extract_text_from_run(
                execution_guard_agent.run(
                    str(
                        {
                            "workspace_root": str(self.workspace),
                            "operation_type": "step_file_write",
                            "allowed_paths": allowed,
                            "candidate_paths": generated_paths,
                        }
                    )
                )
            )
            decision = safe_json_parse(raw)
            if decision.get("allow") is False:
                violations = decision.get("violations", [])
                raise ValueError(f"ExecutionGuard blocked step execution: {violations}")
        except ValueError as exc:
            # If parsing fails we still trust deterministic guard; only raise for explicit block.
            if "ExecutionGuard blocked step execution" in str(exc):
                raise

    # -------------------------
    # Core Execution
    # -------------------------

    def execute_next_step(
        self,
        project_meta: Dict,
        execution_plan: List[Dict],
    ) -> Dict:
        """
        Executes exactly ONE step.
        """

        step = self._next_step(execution_plan)

        if not step:
            return {
                "status": "completed",
                "message": "All steps executed"
            }

        # -------------------------
        # 1. Generate
        # -------------------------

        generator_prompt = {
            "project": project_meta,
            "step": step,
            "existing_files": self._existing_files()
        }

        gen_out = generator_agent.run(
            f"INPUT:\n{generator_prompt}\n\nGenerate ONLY the step outputs."
        )

        gen_raw = getattr(gen_out, "content", str(gen_out))
        gen_data = parse_generation_result(safe_json_parse(gen_raw))

        if gen_data.status != "success":
            self.state_repo.mark_step_failed(
                step["step"],
                gen_data.notes or "Generator failed"
            )
            return {
                "status": "blocked",
                "step": step["step"],
                "reason": "generator_failed"
            }

        # -------------------------
        # 2. Write files
        # -------------------------
        generated_files = [{"path": item.path, "content": item.content} for item in gen_data.files]
        self._guard_generated_files(
            step=step,
            generated_paths=[item["path"] for item in generated_files],
        )

        self._write_files(generated_files)

        # -------------------------
        # 3. Test
        # -------------------------

        test_prompt = {
            "step": step,
            "files": generated_files,
            "workspace": str(self.workspace)
        }

        test_out = test_agent.run(
            f"INPUT:\n{test_prompt}\n\nValidate completion_criteria."
        )

        test_raw = getattr(test_out, "content", str(test_out))
        test_data = parse_validation_result(safe_json_parse(test_raw))

        # -------------------------
        # 4. Fix if needed
        # -------------------------

        if test_data.status != "passed":
            failed_checks = [
                check.details or check.check
                for check in test_data.checks
                if check.result == "fail"
            ]
            editor_prompt = {
                "step": step,
                "errors": failed_checks,
                "files": generated_files
            }

            edit_out = editor_agent.run(
                f"INPUT:\n{editor_prompt}\n\nFix ONLY the broken parts."
            )

            edit_raw = getattr(edit_out, "content", str(edit_out))
            edit_data = parse_edit_result(safe_json_parse(edit_raw))

            if edit_data.status != "success":
                self.state_repo.mark_step_failed(
                    step["step"],
                    "Editor could not fix step"
                )
                return {
                    "status": "blocked",
                    "step": step["step"],
                    "reason": "editor_failed"
                }

            # Apply fixes
            edit_files = [{"path": item.path, "content": item.content} for item in edit_data.files]
            self._guard_generated_files(
                step=step,
                generated_paths=[item["path"] for item in edit_files],
            )
            self._write_files(edit_files)

            # Re-test
            retest_out = test_agent.run(
                f"INPUT:\n{test_prompt}\n\nRe-validate after fixes."
            )

            retest_raw = getattr(retest_out, "content", str(retest_out))
            retest_data = parse_validation_result(safe_json_parse(retest_raw))

            if retest_data.status != "passed":
                self.state_repo.mark_step_failed(
                    step["step"],
                    "Tests still failing after edit"
                )
                return {
                    "status": "blocked",
                    "step": step["step"],
                    "reason": "tests_failed"
                }

        # -------------------------
        # 5. Persist success
        # -------------------------

        self.state_repo.mark_step_completed(
            step["step"],
            files=[f.path for f in gen_data.files]
        )

        return {
            "status": "step_completed",
            "step": step["step"],
            "generated_files": [f.path for f in gen_data.files]
        }
