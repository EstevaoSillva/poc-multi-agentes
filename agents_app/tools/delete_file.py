from pathlib import Path
from agno.tools import Tool

class DeleteFileTool(Tool):
    name = "delete_file"

    def run(self, path: str):
        Path(path).unlink()
        return "File deleted"