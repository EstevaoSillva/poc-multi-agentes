from agents_app.api.models import Session

MAX_INTERACTIONS = 5
MAX_RESPONSE_CHARS = 400


def build_context(session_id: int):
    session = Session.objects.get(id=session_id)

    interactions = (
        session.interactions
        .order_by("-created_at")
        [:MAX_INTERACTIONS]
    )

    # CONTEXTO BASE DO PROJETO (ideation)
    project_context = session.context or {}

    context = {
        # Identidade
        "session_id": session.id,
        "session_title": session.title,

        # Projeto
        "project": {
            "description": project_context.get("description"),
            "category": project_context.get("category"),
            "suggested_stack": project_context.get("suggested_stack"),
            "original_prompt": project_context.get("original_prompt"),
        },

        # Execução
        "recent_interactions": [],
        "files_touched": set(),

        # Planejamento
        "last_intent": None,
        "open_problems": [],
    }

    # HISTÓRICO DE EXECUÇÃO
    for interaction in reversed(interactions):
        item = {
            "intent": interaction.intent,
            "decision": interaction.planner_decision,
            "response_summary": interaction.llm_response[:MAX_RESPONSE_CHARS],
            "tools": []
        }

        for tool in interaction.tools.all():
            item["tools"].append({
                "tool": tool.tool_name,
                "input": tool.input_payload
            })

            path = tool.input_payload.get("path")
            if path:
                context["files_touched"].add(path)

        context["recent_interactions"].append(item)
        context["last_intent"] = interaction.intent

    context["files_touched"] = list(context["files_touched"])

    # DERIVAÇÃO DE ESTADO (simples por enquanto)
    if not context["files_touched"]:
        context["open_problems"].append(
            "Project structure not created yet"
        )

    return context
