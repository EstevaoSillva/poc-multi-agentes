from dotenv import load_dotenv
load_dotenv()

from app.agent_back import backend_agent
from app.agent_front import frontend_agent
from app.agent_team import create_team

def main():
    dev_team = create_team(
        backend_agent=backend_agent,
        frontend_agent=frontend_agent
    )

    dev_team.run(
        """
        Crie um aplicativo web de lista de tarefas (To-Do).
    
        Backend:
        - API REST com FastAPI
        - CRUD de tarefas
        - README.md
    
        Frontend:
        - HTML, CSS e JS
        - Consuma a API
        - README.md
        """,
        stream=False,
        debug=True
    )

if __name__ == "__main__":
    main()