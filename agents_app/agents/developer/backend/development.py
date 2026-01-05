def backend_dev_agent(backend_dir):
    return Agent(
        name="Backend Dev Agent",
        role="Desenvolvimento da API",
        model=dev_model,
        tools=[FileTools(base_dir=backend_dir)],
        instructions=[
            "Criar FastAPI app.",
            "Criar CRUD completo.",
            "Integrar com database existente.",
            "NÃO mexer em infra ou banco.",
        ],
    )