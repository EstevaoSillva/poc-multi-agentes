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

    context = {
        "session_id": session.id,
        "session_title": session.title,
        "recent_interactions": [],
        "files_touched": set(),
        "last_intent": None,
        "open_problems": []
    }

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

            # captura arquivos afetados
            path = tool.input_payload.get("path")
            if path:
                context["files_touched"].add(path)

        context["recent_interactions"].append(item)
        context["last_intent"] = interaction.intent

    context["files_touched"] = list(context["files_touched"])

    return context
