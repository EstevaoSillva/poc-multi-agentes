from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.sql import SQLTools

# 1. Configuração da conexão (Exemplo com Trino via SQLAlchemy)
# Formato: trino://{user}@{host}:{port}/{catalog}/{schema}
db_url = "trino://user@localhost:8080/system/runtime"

# 2. Criar o Agente com a ferramenta SQL pronta
sql_agent = Agent(
    name="Analista de Dados Trino",
    model=OpenAIChat(id="gpt-4o"),
    # O SQLTools introspecta o banco e permite que o agente gere queries
    tools=[SQLTools(db_url=db_url, tables=["nodes", "queries"])], 
    instructions=[
        "Use SQL para responder perguntas.",
        "Se a query falhar, tente corrigir a sintaxe do Trino e tente de novo."
    ],
    markdown=True
)

# 3. O usuário pede em português, o agente gera o SQL
sql_agent.print_response("Quais são os 3 nós (nodes) ativos com mais memória disponível?")