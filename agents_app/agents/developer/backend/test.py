def backend_test_agent(backend_dir):
    return Agent(
        name="Backend Test Agent",
        role="Testes do backend",
        model=test_model,
        tools=[FileTools(base_dir=backend_dir)],
        instructions=[
            "Criar testes com pytest.",
            "Testar CRUD.",
            "NÃO criar código de produção.",
        ],
    )