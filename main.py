from dotenv import load_dotenv

load_dotenv()

from app.agent_back import backend_agent
from app.agent_front import frontend_agent
from app.tech_lead import create_team


def main():
    print("Criando o time de desenvolvimento...")
    dev_team = create_team(
        backend_agent=backend_agent,
        frontend_agent=frontend_agent
    )
    print("Time criado com sucesso!")

    print("Iniciando execução do time...")
    dev_team.run(
        """
        Crie um aplicativo web de lista de tarefas (To-Do).

        Backend:
        - API REST com FastApi
        - CRUD de tarefas
        - requirements.txt
        - README.md

        Frontend:
        - HTML, CSS e JS
        - Consuma a API
        - README.md
        
        É importante que o backend e o frontend sejam salvos em suas respectivas pastas ('my_app/backend' e 'my_app/frontend'), utilizando caminhos relativos para referenciar os arquivos.
        """,
        stream=False,
        debug=True
    )
    print("Execução do time finalizada.")


if __name__ == "__main__":
    print("Iniciando o programa...")
    main()
    print("Programa finalizado.")
