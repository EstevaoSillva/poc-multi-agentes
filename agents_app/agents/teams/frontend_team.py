def build_frontend_team():

    team_front_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

    frontend_dir = Path("./my_app/frontend")

    return Team(
        name="Frontend Team",
        role="Equipe de Frontend",
        model=team_front_model,
        members=[
            frontend_infra_agent(frontend_dir),
            frontend_dev_agent(frontend_dir),
            frontend_test_agent(frontend_dir),
        ],
        instructions=[
            "Frontend estático.",
            "Consumir API do backend.",
        ],
    )
