import json
from pathlib import Path

from agents_app.agents.generator_agent import generator_agent
from agents_app.agents.intent_agent import intent_agent
from agents_app.agents.planner_agent import planner_agent
from agents_app.agents.response_agent import response_agent
from agents_app.agents.reviewer_agent import reviewer_agent
from agents_app.api.models import (
    Interaction,
    ToolExecution,
    PendingAction,
)
from agents_app.context.builder import build_context
from agents_app.context.prompt_adapter import context_to_prompt
from agents_app.services.project_generator import ProjectGeneratorService
from agents_app.tools import (
    read_file,
    write_file,
    delete_file,
    list_files,
    diff_tool,
)
from agents_app.tools.audited_tool import AuditedTool

# ---------------------------------------
# POLICY
# ---------------------------------------
DESTRUCTIVE_TOOLS = {"write_file", "delete_file"}


# ---------------------------------------
# TOOL EXECUTION LOGGER
# ---------------------------------------
class ToolExecutionLog:
    def __init__(self):
        self.executions = []

    def record(self, name, input_payload, output_payload):
        self.executions.append({
            "name": name,
            "input": input_payload,
            "output": output_payload,
        })


# ---------------------------------------
# ORCHESTRATOR
# ---------------------------------------
class CopilotOrchestrator:
    def __init__(self, workspace_path: str):
        self.workspace_root = Path(workspace_path)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.planner_agent = planner_agent

    # -----------------------------------
    # SESSION WORKSPACE
    # -----------------------------------
    def _ensure_session_workspace(self, session_id: int) -> Path:
        session_path = self.workspace_root / "sessions" / f"session_{session_id}"

        for sub in ["frontend", "backend", "shared", "logs"]:
            (session_path / sub).mkdir(parents=True, exist_ok=True)

        return session_path

    # -----------------------------------
    # START PROJECT (NO LLM)
    # -----------------------------------
    def start(self, session_id: int) -> dict:
        """
        Inicializa a estrutura base do projeto.

        """
        from agents_app.api.models import Session

        session = Session.objects.get(id=session_id)
        workspace = self._ensure_session_workspace(session.id)

        context = build_context(session.id)
        context_prompt = context_to_prompt(context)

        generator = ProjectGeneratorService(workspace)

        result = generator.generate_minimal_fastapi_project(
            description=session.context.get("description", "")
        )

        return {
            "message": "Iniciando as tasks...",
            "session_id": session.id,
            "project_path": str(workspace),
            "files_created": result["files"],
        }

    # -----------------------------------
    # SECURITY POLICY
    # -----------------------------------
    def check_policy(self, session_workspace: Path, tool_name: str, args: dict):
        path = args.get("path")
        if not path:
            return

        target = (session_workspace / path).resolve()
        root = session_workspace.resolve()

        if not str(target).startswith(str(root)):
            raise PermissionError(
                f"Acesso fora do workspace da sessão: {target}"
            )

    # -----------------------------------
    # TOOL EXECUTION
    # -----------------------------------
    def execute_tools(self, planner_decision: dict):
        results = []

        for call in planner_decision.get("tools", []):
            tool_name = call["name"]
            args = call.get("args", {})

            self.check_policy(self.session_workspace, tool_name, args)

            tool = next(
                (t for t in planner_agent.tools if t.name == tool_name),
                None
            )

            if not tool:
                raise ValueError(f"Tool '{tool_name}' não registrada")

            output = tool.run(**args)

            results.append({
                "tool": tool_name,
                "output": output,
            })

        return results

    # -----------------------------------
    # MAIN ENTRYPOINT
    # -----------------------------------
    def run(self, session_id: int, user_input: str) -> dict:
        from agents_app.api.models import Session
        session = Session.objects.get(id=session_id)
        self.planner_agent = planner_agent

        # -----------------------------------
        # WORKSPACE
        # -----------------------------------
        self.session_workspace = self._ensure_session_workspace(session.id)

        # -----------------------------------
        # TOOL SETUP
        # -----------------------------------
        tool_log = ToolExecutionLog()

        planner_agent.tools = [
            AuditedTool(
                read_file.ReadFileTool(base_path=self.session_workspace),
                tool_log
            ),
            AuditedTool(
                write_file.WriteFileTool(base_path=self.session_workspace),
                tool_log
            ),
            AuditedTool(
                delete_file.DeleteFileTool(base_path=self.session_workspace),
                tool_log
            ),
            AuditedTool(
                list_files.ListFilesTool(base_path=self.session_workspace),
                tool_log
            ),
            AuditedTool(
                diff_tool.DiffTool(base_path=self.session_workspace),
                tool_log
            ),
        ]

        # -----------------------------------
        # CONTEXT
        # -----------------------------------
        context = build_context(session.id)
        context_prompt = context_to_prompt(context)

        # Persist context snapshot
        (self.session_workspace / "context.json").write_text(
            json.dumps(context, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        # -----------------------------------
        # INTENT
        # -----------------------------------
        intent = intent_agent.run(
            f"""
            {context_prompt}

            User input:
            {user_input}

            Return only the intent.
            """
        ).strip()

        # -----------------------------------
        # PLANNING
        # -----------------------------------
        planner_output = planner_agent.run(
            f"""
            Context:
            {context_prompt}

            Intent: {intent}

            User input:
            {user_input}

            Decide the execution strategy.

            Return STRICT JSON:
            {{
              "strategy": "chat_only | execute_tools",
              "tools": [{{ "name": "...", "args": {{}} }}],
              "description": "..."
            }}
            """
        )

        planner_decision = json.loads(planner_output)

        # -----------------------------------
        # CREATE INTERACTION (EARLY)
        # -----------------------------------
        interaction = Interaction.objects.create(
            session=session,
            user_prompt=user_input,
            intent=intent,
            planner_decision=planner_output,
            llm_response="IN_PROGRESS",
        )

        # -----------------------------------
        # PENDING ACTION (DESTRUCTIVE)
        # -----------------------------------
        for tool in planner_decision.get("tools", []):
            if tool["name"] in DESTRUCTIVE_TOOLS:
                pending = PendingAction.objects.create(
                    session=session,
                    interaction=interaction,
                    tool_name=tool["name"],
                    tool_input=tool.get("args", {}),
                    description=planner_decision.get("description", ""),
                )

                interaction.llm_response = "PENDING_CONFIRMATION"
                interaction.save(update_fields=["llm_response"])

                return {
                    "status": "confirmation_required",
                    "pending_action_id": pending.id,
                    "message": f"O agente deseja executar '{tool['name']}'. Confirma?",
                    "details": pending.tool_input,
                }

        # -----------------------------------
        # EXECUTION
        # -----------------------------------
        tool_results = []
        if planner_decision["strategy"] == "execute_tools":
            tool_results = self.execute_tools(planner_decision)

        # -----------------------------------
        # RESPONSE
        # -----------------------------------
        if intent in (
            Interaction.Intent.GENERATE,
            Interaction.Intent.MODIFY,
        ):
            code = generator_agent.run(user_input)
            review = reviewer_agent.run(code)
            final_result = {
                "generated_code": code,
                "review": review,
            }
        else:
            final_result = response_agent.run(user_input)

        # -----------------------------------
        # FINAL PERSISTENCE
        # -----------------------------------
        interaction.llm_response = json.dumps({
            "tools": tool_results,
            "result": final_result,
        })
        interaction.save(update_fields=["llm_response"])

        for tool in tool_log.executions:
            ToolExecution.objects.create(
                interaction=interaction,
                tool_name=tool["name"],
                input_payload=tool["input"],
                output_payload=tool["output"],
            )

        return {
            "status": "completed",
            "session_id": session.id,
            "interaction_id": interaction.id,
            "intent": intent,
            "tools": tool_results,
            "result": final_result,
        }
