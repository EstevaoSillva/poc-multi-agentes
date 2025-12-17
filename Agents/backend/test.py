from agno.agent import Agent
from agno.tools.file import FileTools

def backend_test_agent(model, backend_dir):
    return Agent(
        name="Backend Test Agent",
        role="Testes do backend",
        model=model,
        tools=[FileTools(base_dir=backend_dir)],
        instructions=[
            "Criar testes com pytest.",
            "Testar CRUD.",
            "NÃO criar código de produção.",
        ],
    )

