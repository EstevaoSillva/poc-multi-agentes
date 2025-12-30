from agno.tools import Tool
from pathlib import Path

class WriteFileTool(Tool):
    name = "write_file"

    def run(self, path: str, content: str):
        Path(path).write_text(content)
        return "File written successfully"