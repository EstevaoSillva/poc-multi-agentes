import difflib
from agno.tools import Tool

class DiffTool(Tool):
    name = "diff_tool"

    def run(self, old: str, new: str):
        return "\n".join(
            difflib.unified_diff(
                old.splitlines(),
                new.splitlines(),
                lineterm=""
            )
        )
