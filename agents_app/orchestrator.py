import json
from pathlib import Path

from agents_app.agents import (
    generator_agent,
    intent_router_agent,
    planner_agent,
    response_agent,
    reviewer_agent,
    build_product_team,
)
from agents_app.api.models import (
    Interaction,
    ToolExecution,
    PendingAction,
)
from agents_app.context.builder import build_context
from agents_app.context.prompt_adapter import context_to_prompt
from agents_app.services.project_generator import ProjectGeneratorService
from agents_app.services.session_memory import SessionMemory
from agents_app.tools.tool_broker import create_broker
from agents_app.tools.tool_registration import register_default_tools
from agents_app.utils import extract_text_from_run, safe_json_parse

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
        self.session_workspace = None
        self.tool_broker = None
        
        # Initialize tool registry
        register_default_tools()

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
        # Prefer passing structured session context (ideation JSON) to the generator
        # so it can read `suggested_stack` and `complexity`. Fall back to the
        # textual context prompt if no structured context is available.
        description_payload = None
        try:
            if session.context and isinstance(session.context, dict):
                description_payload = json.dumps(session.context, ensure_ascii=False)
        except Exception:
            description_payload = None

        description = description_payload or context_prompt

        # Use the newer method that respects planner/intent and suggested_stack
        result = generator.generate_project_from_description(description)

        return {
            "message": "Iniciando as tasks...",
            "session_id": session.id,
            "project_path": str(workspace),
            "files_created": result["files"],
        }

    # -----------------------------------
    # INTENT HANDLING
    # -----------------------------------
    def handle(self, user_input: str):
        return {
            "status": "unsupported",
            "reason": "Use run(session_id, user_input) for actionable orchestration.",
        }

    def _extract_router_intent(self, router_output) -> str:
        raw_text = extract_text_from_run(router_output)
        try:
            data = safe_json_parse(raw_text)
            return str(data.get("intent", "unknown")).strip().lower()
        except ValueError:
            return raw_text.strip().lower()

    def _normalize_intent(self, raw_intent: str) -> str:
        mapping = {
            "create_backend": Interaction.Intent.GENERATE,
            "create_frontend": Interaction.Intent.GENERATE,
            "edit_project": Interaction.Intent.MODIFY,
            "test_project": Interaction.Intent.REVIEW,
            "auto_fix_project": Interaction.Intent.MODIFY,
            "read": Interaction.Intent.READ,
            "generate": Interaction.Intent.GENERATE,
            "review": Interaction.Intent.REVIEW,
            "modify": Interaction.Intent.MODIFY,
            "delete": Interaction.Intent.DELETE,
            "unknown": Interaction.Intent.UNKNOWN,
        }
        return mapping.get((raw_intent or "").strip().lower(), Interaction.Intent.UNKNOWN)

    def _ensure_tool_broker(self, session_id: int, user_id=None):
        if self.session_workspace is None:
            self.session_workspace = self._ensure_session_workspace(session_id)

        if self.tool_broker is None or self.tool_broker.session_id != session_id:
            self.tool_broker = create_broker(
                session_id=session_id,
                workspace_path=self.session_workspace,
                user_id=user_id,
            )
        return self.tool_broker

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
    def execute_tools(self, planner_decision: dict, *, approved: bool = False, user_intent: str | None = None):
        if self.tool_broker is None:
            raise RuntimeError("Tool broker is not initialized for this session")

        results = []

        for call in planner_decision.get("tools", []):
            tool_name = call["name"]
            args = call.get("args", {})

            self.check_policy(self.session_workspace, tool_name, args)
            output, record = self.tool_broker.execute(
                tool_name=tool_name,
                args=args,
                user_intent=user_intent,
                approved=approved,
            )

            results.append({
                "tool": tool_name,
                "status": record.status,
                "error": record.error_message,
                "output": output,
            })

        return results

    # -----------------------------------
    # RUN WITH TEAMS (SPECIALIZED MODE)
    # -----------------------------------
    def run_with_teams(self, session_id: int, user_input: str) -> dict:
        """
        Execute using specialized teams for coordinated development.
        
        This mode uses Product Team which orchestrates Backend and Frontend teams,
        each with specialized agents for infrastructure, development, and testing.
        
        Args:
            session_id: Session ID
            user_input: User request
        
        Returns:
            dict with execution results from teams
        """
        from agents_app.api.models import Session
        
        session = Session.objects.get(id=session_id)
        workspace = self._ensure_session_workspace(session.id)
        memory = SessionMemory(session_id, workspace)
        
        # Retrieve RAG context for this request
        rag_context = memory.get_rag_context(user_input, top_k=3)
        
        # Enhance user input with RAG context
        enhanced_input = f"{rag_context}\n\n{user_input}"
        
        # Build product team with session workspace
        product_team = build_product_team(session_workspace=workspace)
        
        # Execute team with RAG-enhanced input
        try:
            result = product_team.run(enhanced_input)
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "mode": "teams",
                "workspace": str(workspace),
            }
        
        # Record in memory
        memory.add_interaction(
            user_input=user_input,
            response=result,
        )
        return {
            "status": "success",
            "mode": "teams",
            "session_id": session.id,
            "workspace": str(workspace),
            "result": result,
            "memory": memory.get_full_context(),
            "audit": memory.embeddings.get_stats(),
        }
    
    # -----------------------------------
    # MAIN ENTRYPOINT (HYBRID MODE)
    # -----------------------------------
    def run(self, session_id: int, user_input: str, use_teams: bool = None) -> dict:
        """
        Execute orchestration with intent-based selection (Opção B).
        
        If use_teams is not specified, automatically selects based on intent:
        - CREATE intents → use teams (specialized)
        - Other intents → use agents (flexible)
        
        Args:
            session_id: Session ID
            user_input: User request
            use_teams: Force use of teams (None = auto-select)
        
        Returns:
            dict with execution results
        """
        # Detect intent first
        intent_output = intent_router_agent.run(
            f"{user_input}\n\nClassify the intent (create_backend, create_frontend, edit_project, test_project, unknown)"
        )
        detected_intent = self._extract_router_intent(intent_output)
        
        # Auto-select mode if not specified
        if use_teams is None:
            use_teams = detected_intent in ["create_backend", "create_frontend"]
        
        # Use teams for creation intents
        if use_teams:
            return self.run_with_teams(session_id, user_input)
        
        # Otherwise use traditional agent pipeline
        return self.run_with_agents(session_id, user_input)
    
    def run_with_agents(self, session_id: int, user_input: str) -> dict:
        """
        Execute using traditional agent pipeline (original implementation).
        
        More flexible for editing, testing, and general requests.
        """
        from agents_app.api.models import Session
        session = Session.objects.get(id=session_id)
        self.planner_agent = planner_agent

        # -----------------------------------
        # WORKSPACE & MEMORY & TOOLS
        # -----------------------------------
        self.session_workspace = self._ensure_session_workspace(session.id)
        memory = SessionMemory(session_id, self.session_workspace)
        
        tool_broker = self._ensure_tool_broker(
            session_id=session_id,
            user_id=getattr(session, "created_by_user_id", None),
        )

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
        
        # Store metadata in memory
        if hasattr(session, 'description'):
            memory.set_metadata("project_description", session.description)
        if hasattr(session, 'category'):
            memory.set_metadata("project_category", session.category)

        # -----------------------------------
        # INTENT
        # -----------------------------------
        raw_intent_output = intent_router_agent.run(
            f"""
            {context_prompt}

            User input:
            {user_input}

            Return STRICT JSON with intent/confidence/reason.
            """
        )
        raw_intent = self._extract_router_intent(raw_intent_output)
        intent = self._normalize_intent(raw_intent)

        # -----------------------------------
        # PLANNING (with RAG)
        # -----------------------------------
        # Retrieve RAG context based on user input
        rag_context = memory.get_rag_context(user_input, top_k=3)
        
        planner_output = planner_agent.run(
            f"""
            Context:
            {context_prompt}

            RAG Retrieved Context:
            {rag_context}

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

        planner_decision_raw = extract_text_from_run(planner_output)
        planner_decision = safe_json_parse(planner_decision_raw)
        
        # Record in memory for future context
        memory.add_interaction(
            user_input=user_input,
            intent={"raw": raw_intent, "normalized": intent},
            planner_decision=planner_decision,
        )

        # -----------------------------------
        # CREATE INTERACTION (EARLY)
        # -----------------------------------
        interaction = Interaction.objects.create(
            session=session,
            user_prompt=user_input,
            intent=intent,
            planner_decision=planner_decision,
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
        if planner_decision.get("strategy") == "execute_tools":
            tool_results = self.execute_tools(
                planner_decision,
                user_intent=raw_intent,
            )

        # -----------------------------------
        # RESPONSE (with RAG)
        # -----------------------------------
        if intent in (
            Interaction.Intent.GENERATE,
            Interaction.Intent.MODIFY,
        ):
            code = extract_text_from_run(
                generator_agent.run(f"{rag_context}\n\nUser request:\n{user_input}")
            )
            review = extract_text_from_run(reviewer_agent.run(code))
            final_result = {
                "generated_code": code,
                "review": review,
            }
        else:
            final_result = extract_text_from_run(
                response_agent.run(f"{rag_context}\n\nUser request:\n{user_input}")
            )

        # -----------------------------------
        # FINAL PERSISTENCE
        # -----------------------------------
        interaction.llm_response = json.dumps({
            "tools": tool_results,
            "result": final_result,
        })
        interaction.save(update_fields=["llm_response"])

        # Persist broker audit log
        for execution_record in tool_broker.get_execution_log():
            ToolExecution.objects.create(
                interaction=interaction,
                tool_name=execution_record.tool_name,
                input_payload=execution_record.args,
                output_payload=execution_record.result or {},
            )

        # Update memory with final response
        memory.add_interaction(
            user_input=user_input,
            response=final_result,
        )

        return {
            "status": "completed",
            "session_id": session.id,
            "interaction_id": interaction.id,
            "intent": intent,
            "tools": tool_results,
            "result": final_result,
            "memory": memory.get_full_context(),
            "audit": tool_broker.export_audit(),
        }
