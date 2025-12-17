from agno.agent import Agent
from agno.tools.file import FileTools

def frontend_dev_agent(model, frontend_dir):
    return Agent(
        name="Frontend Dev Agent",
        role="Desenvolvimento da interface",
        model=model,
        tools=[FileTools(base_dir=frontend_dir)],
        instructions=[
            "Implementar interface de lista de tarefas.",
            "Usar apenas HTML5, CSS3 e JavaScript puro.",
            "Consumir API REST em http://127.0.0.1:8000.",
            "Implementar CRUD completo.",
            "Não alterar estrutura criada pelo Infra Agent.",
            "Não criar novos arquivos sem necessidade.",
            "Não criar README.",
        ],
    )
