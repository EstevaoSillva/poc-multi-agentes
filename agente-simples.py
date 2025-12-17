from agno.agent import Agent
from agno.models.groq import Groq

from dotenv import load_dotenv

# Carrega as chaves do arquivo .env
load_dotenv()

# 1. Definição do Agente
dev_agent = Agent(
    name="Dev Helper", # Nome do agente
    role="Especialista em Python", # Função do agente
    model=Groq(id="openai/gpt-oss-120b"), # Modelo do agente
    instructions=[
        "Sempre forneça código limpo e tipado.",
        "Explique brevemente o 'porquê' da solução."
    ], # Instruções
    markdown=True, # Formata a saída em Markdown
)

# 2. Execução
dev_agent.print_response("Como inverto uma lista em Python de forma eficiente?")


