from agno.agent import Agent
from agents_app.llm.ollama_provider import get_llm
from agents_app.tools.diff_tool import DiffTool
from agents_app.tools.delete_file import DeleteFileTool
from agents_app.tools.list_files import ListFilesTool
from agents_app.tools.read_file import ReadFileTool
from agents_app.tools.write_file import WriteFileTool


planner_agent = Agent(
    name="PlannerAgent",
    model=get_llm(),
    tools=[
        DiffTool(),
        ReadFileTool(),
        WriteFileTool(),
        DeleteFileTool(),
        ListFilesTool(),
    ],
    instructions="""
            You decide which tools to use.
            Never modify files without showing diff.
        """
)