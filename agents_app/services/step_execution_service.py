from pathlib import Path
from typing import Dict, List

from agents_app.agents.generator_agent import generator_agent
from agents_app.agents.actions.test_agent import test_agent
from agents_app.agents.actions import editor_agent
from agents_app.state.project_state_repository import ProjectStateRepository
from agents_app.utils import safe_json_parse


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
        gen_data = safe_json_parse(gen_raw)

        if gen_data.get("status") != "success":
            self.state_repo.mark_step_failed(
                step["step"],
                gen_data.get("notes", "Generator failed")
            )
            return {
                "status": "blocked",
                "step": step["step"],
                "reason": "generator_failed"
            }

        # -------------------------
        # 2. Write files
        # -------------------------

        self._write_files(gen_data["files"])

        # -------------------------
        # 3. Test
        # -------------------------

        test_prompt = {
            "step": step,
            "files": gen_data["files"],
            "workspace": str(self.workspace)
        }

        test_out = test_agent.run(
            f"INPUT:\n{test_prompt}\n\nValidate completion_criteria."
        )

        test_raw = getattr(test_out, "content", str(test_out))
        test_data = safe_json_parse(test_raw)

        # -------------------------
        # 4. Fix if needed
        # -------------------------

        if test_data.get("status") != "passed":
            editor_prompt = {
                "step": step,
                "errors": test_data.get("errors"),
                "files": gen_data["files"]
            }

            edit_out = editor_agent.run(
                f"INPUT:\n{editor_prompt}\n\nFix ONLY the broken parts."
            )

            edit_raw = getattr(edit_out, "content", str(edit_out))
            edit_data = safe_json_parse(edit_raw)

            if edit_data.get("status") != "success":
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
            self._write_files(edit_data["files"])

            # Re-test
            retest_out = test_agent.run(
                f"INPUT:\n{test_prompt}\n\nRe-validate after fixes."
            )

            retest_raw = getattr(retest_out, "content", str(retest_out))
            retest_data = safe_json_parse(retest_raw)

            if retest_data.get("status") != "passed":
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
            files=[f["path"] for f in gen_data["files"]]
        )

        return {
            "status": "step_completed",
            "step": step["step"],
            "generated_files": [f["path"] for f in gen_data["files"]]
        }