POC Multi-Agentes com Django & Agno

Este projeto é uma Prova de Conceito (POC) de um sistema multi-agente capaz de planejar, gerar e gerenciar projetos FastAPI e Frontend de forma automatizada.

Tecnologias Utilizadas

O sistema utiliza as seguintes tecnologias e componentes:

•
Django: Para a camada de API, persistência e orquestração.

•
Agno (antigo Phidata): Para coordenação dos agentes de IA.

•
Ollama: Como provedor local de LLM (Large Language Model).

•
Docker: Para infraestrutura de banco de dados.

🚀 Como Executar o Projeto

1. Pré-requisitos

Certifique-se de ter instalado:

•
Python 3.12+

•
Docker e Docker Compose

•
Ollama (LLM local)

Instalação do Ollama: 👉 https://ollama.com

Após instalar, baixe o modelo configurado no projeto (exemplo):

Bash


ollama pull mistral-small



⚠️ Atenção: Verifique o modelo configurado no arquivo ollama_provider.py.

2. Configuração do Ambiente

Clone o repositório e acesse a pasta do projeto.

Crie e ative o ambiente virtual:

Bash


python -m venv venv


Linux / macOS:

Bash


source venv/bin/activate


Windows:

Bash


.\venv\Scripts\activate


Instale as dependências:

Bash


pip install -r requirements.txt


3. Configuração do Banco de Dados

Antes de executar as migrações, suba o banco de dados PostgreSQL via Docker Compose:

Bash


docker compose -f compose/docker-compose-postgres.yml up -d


Com o banco ativo, execute as migrações do Django:

Bash


python manage.py migrate


(Opcional) Crie um superusuário para acessar o Django Admin:

Bash


python manage.py createsuperuser


4. Executando o Servidor

Inicie o servidor de desenvolvimento do Django:

Bash


python manage.py runserver


A API estará disponível em:

http://127.0.0.1:8000

🛠️ Estrutura do Projeto

Plain Text


agents_app/
├── agents/                # Definição dos agentes (Ideation, Planner, Generator, etc)
├── api/                   # Views e modelos da API (Sessões, Interações, Logs)
├── context/               # Construção e adaptação de contexto
├── services/              # Serviços auxiliares (ex: ProjectGeneratorService)
├── tools/                 # Ferramentas disponíveis para os agentes
├── orchestrator.py        # Orquestrador principal (CopilotOrchestrator)
workspace/
└── sessions/              # Projetos gerados, organizados por sessão
compose/
└── docker-compose-postgres.yml


🤖 Fluxo de Trabalho

O processo de geração de projetos segue as seguintes etapas:

1.
Ideação O AppIdeationAgent recebe um prompt do usuário e define:

•
Nome da aplicação

•
Categoria

•
Stack sugerida



2.
Orquestração O CopilotOrchestrator:

•
Cria o workspace da sessão

•
Inicializa diretórios base

•
Garante isolamento por sessão



3.
Geração O ProjectGeneratorService utiliza o CodeGeneratorAgent para:

•
Gerar arquivos do backend (FastAPI)

•
Criar frontend básico (HTML/CSS)

•
Garantir que todas as pastas e arquivos necessários existam



4.
Iteração Via API, o usuário pode solicitar alterações:

•
O PlannerAgent decide a estratégia

•
As Tools executam alterações no workspace

•
Tudo é auditado e persistido



📂 Projetos Gerados

Os projetos criados pelos agentes ficam em:

Plain Text


workspace/sessions/session_<id>/


Exemplo de Estrutura de Sessão:

Plain Text


workspace/sessions/session_15/
├── backend/
├── frontend/
├── shared/
└── logs/


Cada sessão é isolada, garantindo segurança e rastreabilidade.

📝 Notas de Desenvolvimento

Logs e Auditoria

•
Todas as interações com LLMs são persistidas.

•
Execuções de ferramentas são registradas no banco.

•
É possível auditar quem fez o quê e quando.

Segurança

O orquestrador aplica uma política de segurança rigorosa:

•
Os agentes não podem acessar arquivos fora da sessão.

•
Escrita e deleção passam por validação (check_policy).

•
Ações destrutivas podem exigir confirmação.

