backend_team = build_backend_team()
frontend_team = build_frontend_team()

product_team = Team(
    name="Product Team",
    role="Coordenação geral",
    model=po_model,
    members=[backend_team, frontend_team],
    instructions=[
        "Executar backend primeiro.",
        "Após backend pronto, executar frontend.",
        "Garantir integridade do projeto.",
    ],
)
