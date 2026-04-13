import unittest

from agents_app.contracts import (
    parse_edit_result,
    parse_generation_result,
    parse_intent_decision,
    parse_plan_decision,
    parse_validation_result,
)


class TestAgentContracts(unittest.TestCase):
    def test_parse_generation_result_success(self):
        payload = {
            "status": "success",
            "files": [{"path": "backend/main.py", "content": "print('ok')"}],
            "notes": "done",
        }
        result = parse_generation_result(payload)
        self.assertEqual(result.status, "success")
        self.assertEqual(len(result.files), 1)
        self.assertEqual(result.files[0].path, "backend/main.py")

    def test_parse_validation_result_normalizes_pass_alias(self):
        payload = {
            "status": "pass",
            "step": 1,
            "checks": [{"check": "exists", "result": "passed", "details": "ok"}],
        }
        result = parse_validation_result(payload)
        self.assertEqual(result.status, "passed")
        self.assertEqual(result.step, 1)
        self.assertEqual(result.checks[0].result, "pass")

    def test_parse_edit_result_accepts_changes_alias(self):
        payload = {
            "status": "success",
            "changes": [{"path": "frontend/index.html", "content": "<html></html>"}],
        }
        result = parse_edit_result(payload)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.files[0].path, "frontend/index.html")

    def test_parse_intent_decision_requires_numeric_confidence(self):
        payload = {"intent": "generate", "confidence": "abc", "reason": "x"}
        with self.assertRaises(ValueError):
            parse_intent_decision(payload)

    def test_parse_plan_decision_filters_invalid_tools(self):
        payload = {
            "strategy": "execute_tools",
            "tools": [
                {"name": "read_file", "args": {"path": "a.txt"}},
                {"name": "", "args": {"path": "b.txt"}},
                {"args": {"path": "c.txt"}},
                "invalid",
            ],
        }
        result = parse_plan_decision(payload)
        self.assertEqual(result.strategy, "execute_tools")
        self.assertEqual(len(result.tools), 1)
        self.assertEqual(result.tools[0]["name"], "read_file")

    def test_parse_generation_result_rejects_invalid_files(self):
        payload = {"status": "success", "files": [{"path": "", "content": "x"}]}
        with self.assertRaises(ValueError):
            parse_generation_result(payload)


if __name__ == "__main__":
    unittest.main()
