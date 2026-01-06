from dotenv import load_dotenv
load_dotenv()

from app.files_structrure_agent import structure_agent
from app.agent_back import backend_agent
from app.agent_front import frontend_agent
from app.agent_test import test_agent
from app.tech_lead import create_team


def main():
    print("Criando o time de desenvolvimento...")

    dev_team = create_team(
        structure_agent=structure_agent,
        backend_agent=backend_agent,
        frontend_agent=frontend_agent,
        test_agent=test_agent
    )

    print("Time criado com sucesso!")
    print("Iniciando execução do time...")

    dev_team.run(
        """
        Desenvolva uma aplicação web de Lista de Tarefas (To-Do List).
        
        Requisitos funcionais:
        - Criar, listar, atualizar e remover tarefas (CRUD)
        - Persistência simples (em memória ou arquivo)
        
        Requisitos técnicos:
        - Backend com FastAPI
        - Frontend com HTML, CSS e JavaScript puro
        - Comunicação via API REST
        - Backend rodando na porta 8000
        
        Regras importantes:
        - Toda a estrutura do projeto deve ser criada pelo agente de estrutura
        - Backend e frontend devem seguir estritamente o contract.json
        - Os agentes nao devem criar arquivos .gitkeep ou similares
        - Nenhum agente deve assumir caminhos
        - A aplicação só é considerada pronta se os testes passarem
        """,
        stream=False,
        debug=True
    )

    print("Execução do time finalizada.")

if __name__ == "__main__":
    print("Iniciando o programa...")
    main()
    print("Programa finalizado.")
