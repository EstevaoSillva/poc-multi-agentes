from agno.tools import Tool
from pathlib import Path

class ReadFileTool(Tool):
    name = "read_file"
    description = "Read file content"

    def run(self, path: str):
        return Path(path).read_text()