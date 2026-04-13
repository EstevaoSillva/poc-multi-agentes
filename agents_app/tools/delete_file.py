from pathlib import Path
from agno.tools import Toolkit

class DeleteFileTool(Toolkit):
    name = "delete_file"

    def run(self, path: str):
        Path(path).unlink()
        return "File deleted"