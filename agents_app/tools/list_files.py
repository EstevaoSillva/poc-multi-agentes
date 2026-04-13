from agno.tools import Toolkit
from pathlib import Path


class ListFilesTool(Toolkit):
    name = "list_files"

    def run(self, base_path: str):
        return [str(p) for p in Path(base_path).rglob("*")]