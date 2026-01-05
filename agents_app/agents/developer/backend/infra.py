def backend_infra_agent(backend_dir):
    return Agent(
        name="Backend Infra Agent",
        role="Infraestrutura do backend",
        model=infra_model,
        tools=[FileTools(base_dir=backend_dir)],
        instructions=[
            "Criar estrutura base do backend.",
            "Criar requirements.txt.",
            "Criar README.md.",
            "NÃO criar banco, modelos ou endpoints.",
            "NUNCA criar pasta raiz do projeto.",
        ],
    )