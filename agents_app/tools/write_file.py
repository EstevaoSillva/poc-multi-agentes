from agno.tools import Toolkit
from pathlib import Path

class WriteFileTool(Toolkit):
    name = "write_file"

    def run(self, path: str, content: str):
        Path(path).write_text(content)
        return "File written successfully"