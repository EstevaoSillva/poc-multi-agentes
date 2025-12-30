from agno.tools import Tool
from pathlib import Path


class ListFilesTool(Tool):
    name = "list_files"

    def run(self, base_path: str):
        return [str(p) for p in Path(base_path).rglob("*")]