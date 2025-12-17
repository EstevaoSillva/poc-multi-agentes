from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.duckduckgo import DuckDuckGoTools
from dotenv import load_dotenv
import json


# 2. Carrega as chaves do arquivo .env
load_dotenv()

# Sub-agente 1
web_agent = Agent(
    name="Web Searcher",
    role="Pesquisador Web",
    model=Groq(id="openai/gpt-oss-120b"),
    instructions="Pesquise informações atuais na internet.",
    tools=[DuckDuckGoTools()],
)

# Sub-agente 2
finance_agent = Agent(
    name="Finance Analyst",
    role="Analista Financeiro",
    model=Groq(id="openai/gpt-oss-120b"),
    instructions="Analise tabelas financeiras e calcule métricas.",
)

# Agente Líder (Team Leader)
# Ele possui os outros agentes na lista 'team'
lider_agent = Agent(
    name="Team Lead",
    role="Gerente de Produto",
    model=Groq(id="openai/gpt-oss-120b"),
    # Nota: a classe Agent não aceita argumento `team` — a orquestração entre
    # sub-agentes deve ser feita explicitamente no código (ver runner/exemplo).
    instructions=[
        "Você coordena a equipe.",
        "Delegue a pesquisa para o Web Searcher.",
        "Delegue cálculos para o Finance Analyst.",
        "Compile a resposta final."
    ],
    # show_tool_calls foi removido pois não é argumento suportado pela API atual
    markdown=True
)

lider_agent.print_response(
    "Pesquise o preço das ações da Apple hoje e calcule o P/L estimado com base no lucro do ano passado."
)