"""
Standard tool registration - initialize registry with default tools.
"""

from agents_app.tools.tool_broker import (
    get_tool_registry,
    ToolPermission,
)
from agents_app.tools import (
    read_file,
    write_file,
    delete_file,
    list_files,
    diff_tool,
)


def register_default_tools():
    """Register all standard tools in the default registry."""
    registry = get_tool_registry()

    # Module-level wrappers (picklable) that instantiate tool classes and call their run()
    def read_file_impl(path: str):
        return read_file.ReadFileTool().run(path=path)

    def write_file_impl(path: str, content: str):
        return write_file.WriteFileTool().run(path=path, content=content)

    def delete_file_impl(path: str):
        return delete_file.DeleteFileTool().run(path=path)

    def list_files_impl(base_path: str):
        return list_files.ListFilesTool().run(base_path=base_path)

    def diff_impl(old: str, new: str):
        return diff_tool.DiffTool().run(old=old, new=new)

    # File reading tool (safe)
    registry.register(
        name="read_file",
        impl=read_file_impl,
        description="Read contents of a file",
        category="file",
        permission=ToolPermission.PUBLIC,
        requires_approval=False,
        sandbox_required=True,
        max_timeout_sec=10,
        arg_schema={"path": "str"},
    )

    # File writing tool (destructive)
    registry.register(
        name="write_file",
        impl=write_file_impl,
        description="Write or create a file",
        category="file",
        permission=ToolPermission.DESTRUCTIVE,
        requires_approval=True,
        sandbox_required=True,
        max_timeout_sec=10,
        arg_schema={"path": "str", "content": "str"},
    )

    # File deletion tool (destructive)
    registry.register(
        name="delete_file",
        impl=delete_file_impl,
        description="Delete a file",
        category="file",
        permission=ToolPermission.DESTRUCTIVE,
        requires_approval=True,
        sandbox_required=True,
        max_timeout_sec=10,
        arg_schema={"path": "str"},
    )

    # Directory listing tool (safe)
    registry.register(
        name="list_files",
        impl=list_files_impl,
        description="List files in a directory",
        category="file",
        permission=ToolPermission.PUBLIC,
        requires_approval=False,
        sandbox_required=True,
        max_timeout_sec=10,
        arg_schema={"base_path": "str"},
    )

    # Diff tool (safe)
    registry.register(
        name="diff",
        impl=diff_impl,
        description="Generate diff between two versions",
        category="code",
        permission=ToolPermission.PUBLIC,
        requires_approval=False,
        sandbox_required=True,
        max_timeout_sec=15,
        arg_schema={"old": "str", "new": "str"},
    )


# Auto-register on import
register_default_tools()
