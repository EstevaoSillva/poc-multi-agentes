from agno.agent import Agent
from agno.team import Team
from agno.models.groq import Groq
from agno.tools.file import FileTools # Ferramenta essencial para escrever código
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configurar logging para ver todos os detalhes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

local_model = Groq(id="openai/gpt-oss-120b")

PROJECT_ROOT = Path("my_app").resolve()
BACKEND_ROOT = PROJECT_ROOT / "backend"
FRONTEND_ROOT = PROJECT_ROOT / "frontend"

BACKEND_ROOT.mkdir(parents=True, exist_ok=True)
FRONTEND_ROOT.mkdir(parents=True, exist_ok=True)




# 3. Agente de Frontend
frontend_agent = Agent(
    name="Frontend Engineer",
    role="Desenvolvedor sênior de Angular e UI",
    model=local_model,
    tools=[FileTools(base_dir=FRONTEND_ROOT)], # Onde ele pode salvar arquivos
    instructions=[
        "Você DEVE usar a ferramenta FileTools para criar arquivos reais.",
        "Crie index.html, styles.css e app.js.",
        "Use HTML5, CSS3 e JavaScript puro.",
        "A API base URL deve ser http://127.0.0.1:8000.",
        "Implemente chamadas fetch para CRUD.",
        "Todos os arquivos DEVEM estar em UTF-8.",
        "Não leia arquivos existentes; sobrescreva.",
        "Todos os arquivos DEVEM ser criados diretamente no diretório atual (frontend).",
        "Não crie subpastas redundantes.",
    ],
    debug_mode=True,
    debug_level=2,
)

# 4. O Orquestrador (Team Leader)
# Este agente controla os outros.
dev_team = Team(
    name="Tech Lead",
    role="Gerente de Produto e Arquiteto de Software",
    model=local_model,
    members=[backend_agent, frontend_agent], # Aqui definimos a equipe
    instructions=[
        "Você recebe uma solicitação de aplicativo do usuário.",
        "1. Quebre a solicitação em tarefas de backend e frontend.",
        "2. Peça ao Backend Engineer para configurar a estrutura base.",
        "3. Peça ao Frontend Engineer para criar a interface.",
        "4. Garanta que os arquivos sejam salvos usando as ferramentas disponíveis.",
        "Não escreva o código você mesmo, delegue para os especialistas."
    ],
    markdown=True,
)


# 5. Execução
print("Iniciando a equipe de desenvolvimento...")
dev_team.run(
    """
        Crie um aplicativo web simples de lista de tarefas (To-Do List) com as seguintes funcionalidades:
        
        Backend Engenieer 
           - Crie com API REST para gerenciar tarefas (criar, ler, atualizar, deletar).
           - Use FastAPI para o backend 
           - Crie um README.md com instruções de configuração e execução.

        Frontend Engineer
           - Use HTML5/CSS3/JavaScript para o frontend.
           - Crie um README.md com instruções de configuração e execução.
           - Crie com uma interface amigável para interagir com a API.
           - Salve todos os arquivos necessários no sistema usando FileTools dentro da pasta my_app.
        
        Crie um README.md com instruções de configuração e execução.
    """,
    stream=False,
    debug=True
)


print("Fim do desenvolvimento...")
