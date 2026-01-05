def build_backend_team():


    team_back_model = Ollama(
    id=os.getenv("OLLAMA_MODEL")
)

    backend_dir = Path("./my_app/backend")

    return Team(
        name="Backend Team",
        role="Equipe de Backend",
        model=team_back_model,
        members=[
            backend_infra_agent(backend_dir),
            backend_db_agent(backend_dir),
            backend_dev_agent(backend_dir),
            backend_test_agent(backend_dir),
        ],
        instructions=[
            "Executar na ordem: Infra → Database → Dev → Test.",
            "Cada agente respeita sua responsabilidade.",
        ],
    )
