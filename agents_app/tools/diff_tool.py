import difflib
from agno.tools import Toolkit

class DiffTool(Toolkit):
    name = "diff_tool"

    def run(self, old: str, new: str):
        return "\n".join(
            difflib.unified_diff(
                old.splitlines(),
                new.splitlines(),
                lineterm=""
            )
        )
