def context_to_prompt(context: dict) -> str:
    prompt = []

    # Papel
    prompt.append(
        "You are an autonomous planning agent responsible for deciding the next action."
    )

    # Identidade da sessão
    title = context.get('session_title') or context.get('app_name') or "Untitled Project"
    prompt.append(f"Session title: {title}")

    # Projeto
    project = context.get("project", {})
    if project:
        prompt.append("Project context:")
        if project.get("description"):
            prompt.append(f"- Description: {project['description']}")
        if project.get("category"):
            prompt.append(f"- Category: {project['category']}")
        if project.get("suggested_stack"):
            prompt.append(f"- Stack: {project['suggested_stack']}")

    # Estado atual
    prompt.append("Current state:")

    if context.get("files_touched"):
        prompt.append(
            f"- Files created or modified: {', '.join(context['files_touched'])}"
        )
    else:
        prompt.append("- No files have been created yet")

    if context.get("open_problems"):
        prompt.append("Open problems:")
        for p in context["open_problems"]:
            prompt.append(f"- {p}")

    # Histórico resumido
    if context.get("recent_interactions"):
        prompt.append("Recent actions:")
        for i in context["recent_interactions"]:
            prompt.append(
                f"- Intent: {i['intent']}"
            )

    # Instrução explícita
    prompt.append(
        "Based on the project context and current state, decide the next best action."
    )

    return "\n".join(prompt)
