from agno.tools import Toolkit
from pathlib import Path

class ReadFileTool(Toolkit):
    name = "read_file"
    description = "Read file content"

    def run(self, path: str):
        return Path(path).read_text()