

def context_to_prompt(context: dict) -> str:
    prompt = []

    prompt.append("You are continuing an ongoing session.")
    prompt.append(f"Session title: {context['session_title']}")

    if context["files_touched"]:
        prompt.append(
            f"Files recently touched: {', '.join(context['files_touched'])}"
        )

    prompt.append("Recent decisions:")

    for i in context["recent_interactions"]:
        prompt.append(
            f"- Intent: {i['intent']} | Decision: {i['decision']}"
        )

    return "\n".join(prompt)
