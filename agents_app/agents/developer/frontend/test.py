def frontend_test_agent(frontend_dir):
    return Agent(
        name="Frontend Test Agent",
        role="Testes e validação do frontend",
        model=test_model,
        tools=[FileTools(base_dir=frontend_dir)],
        instructions=[
            "Validar se a UI carrega corretamente.",
            "Verificar chamadas fetch.",
            "Criar checklist de testes manuais.",
            "Não alterar código da aplicação.",
            "Documentar falhas no README.md.",
        ],
    )
