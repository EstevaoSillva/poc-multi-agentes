from agents_app.services.test_service import TestService
from agents_app.services.editor_service import EditorService


class AutoFixService:
    def __init__(self, workspace, max_attempts: int = 3):
        self.workspace = workspace
        self.max_attempts = max_attempts
        self.test_service = TestService(workspace)
        self.editor_service = EditorService(workspace)

    def run(self) -> dict:
        attempts = 0
        history = []

        while attempts < self.max_attempts:
            test_result = self.test_service.run()
            history.append(test_result)

            if test_result["status"] == "pass":
                return {
                    "status": "success",
                    "attempts": attempts + 1,
                    "history": history
                }

            errors = test_result.get("errors", [])

            if not errors:
                return {
                    "status": "failed",
                    "reason": "Tests failed but no errors reported",
                    "history": history
                }

            self.editor_service.edit(
                instruction=self._build_fix_instruction(errors)
            )

            attempts += 1

        return {
            "status": "failed",
            "reason": "Max auto-fix attempts reached",
            "attempts": attempts,
            "history": history
        }

    def _build_fix_instruction(self, errors: list[str]) -> str:
        joined = "\n".join(f"- {e}" for e in errors)
        return f"""
            Fix ONLY the following issues:
            
            {joined}
            
            Rules:
            - Do NOT refactor unrelated code
            - Do NOT introduce new features
            - Maintain runtime correctness
        """