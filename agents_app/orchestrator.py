import json

from agents_app.agents.generator_agent import generator_agent
from agents_app.agents.intent_agent import intent_agent
from agents_app.agents.planner_agent import planner_agent
from agents_app.agents.response_agent import response_agent
from agents_app.agents.reviewer_agent import reviewer_agent
from agents_app.api.models import Session, Interaction, ToolExecution, PendingAction
from agents_app.context.builder import build_context
from agents_app.context.prompt_adapter import context_to_prompt
from agents_app.tools import delete_file, diff_tool, list_files, read_file, write_file
from agents_app.tools.audited_tool import AuditedTool

DESTRUCTIVE_TOOLS = {
    "write_file",
    "delete_file",
}


class ToolExecutionLog:
    def __init__(self):
        self.executions = []

    def record(self, name, input_payload, output_payload):
        self.executions.append({
            "name": name,
            "input": input_payload,
            "output": output_payload
        })

class CopilotOrchestrator:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def run(self, session_id: int, user_input: str) -> dict:
        session = Session.objects.get(id=session_id)

        # TOOL LOGGER VIVO DURANTE TODA EXECUÇÃO
        tool_log = ToolExecutionLog()

        tools = [
            AuditedTool(read_file.ReadFileTool(), tool_log),
            AuditedTool(write_file.WriteFileTool(), tool_log),
            AuditedTool(delete_file.DeleteFileTool(), tool_log),
            AuditedTool(list_files.ListFilesTool(), tool_log),
            AuditedTool(diff_tool.DiffTool(), tool_log),
        ]

        # INJEÇÃO REAL DAS TOOLS
        planner_agent.tools = tools


        # Build context
        context = build_context(session.id)
        context_prompt = context_to_prompt(context)

        # Detect intent
        intent = intent_agent.run(
            f"""{context_prompt}
                User input:
                {user_input}
                Return only the intent.
            """
        ).strip()

        # Planner decision
        planner_output = planner_agent.run(
            f"""
                Context:
                {context_prompt}
                
                Intent: {intent}
                
                User input:
                {user_input}
                
                Decide the execution strategy.
                Return a JSON with:
                - strategy
                - tools
                - description
            """
        )

        # aqui assumimos JSON bem-formado
        planner_decision = json.loads(planner_output)
        requested_tools = planner_decision.get("tools", [])


        for tool in requested_tools:
            tool_name = tool.get("name")
            tool_input = tool.get("input", {})

            if tool_name in DESTRUCTIVE_TOOLS:
                pending = PendingAction.objects.create(
                    session=session,
                    tool_name=tool_name,
                    tool_input=tool_input,
                    description=planner_decision.get("description", "")
                )

                # ⛔ NÃO cria Interaction
                return {
                    "status": "confirmation_required",
                    "pending_action_id": pending.id,
                    "message": f"O agente deseja executar '{tool_name}'. Confirma?",
                    "details": {
                        "tool": tool_name,
                        "input": tool_input,
                        "description": pending.description
                    }
                }

        # -------- EXECUÇÃO REAL (SEGURA) --------
        final_result = None

        if intent == Interaction.Intent.READ:
            final_result = planner_agent.run(
                f"Execute the read operation for: {user_input}"
            )

        elif intent in [Interaction.Intent.GENERATE, Interaction.Intent.MODIFY]:
            code = generator_agent.run(user_input)
            review = reviewer_agent.run(code)
            final_result = {
                "generated_code": code,
                "review": review
            }

        elif intent == Interaction.Intent.DELETE:
            final_result = planner_agent.run(
                f"Execute delete operation: {user_input}"
            )

        else:
            final_result = response_agent.run(user_input)

        # -------- PERSISTÊNCIA FINAL --------
        # AGORA SIM cria Interaction
        interaction = Interaction.objects.create(
            session=session,
            user_prompt=user_input,
            intent=intent,
            planner_decision=planner_output,
            llm_response=str(final_result)
        )

        # Persistir tools realmente executadas
        for tool in tool_log.executions:
            ToolExecution.objects.create(
                interaction=interaction,
                tool_name=tool["name"],
                input_payload=tool["input"],
                output_payload=tool["output"]
            )

        return {
            "status": "completed",
            "session_id": session.id,
            "intent": intent,
            "result": final_result
        }
