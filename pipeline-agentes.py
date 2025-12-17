from agno.agent import Agent
from agno.models.groq import Groq

from dotenv import load_dotenv
load_dotenv()


# Agente 1: Gerador de Dados (Simulado)
analista = Agent( # Cria um agente
    name="Analista", # Nome do agente
    role="Analista de Dados", # Função do agente
    model=Groq(id="openai/gpt-oss-120b"), # Modelo do agente
    instructions="Gere um pequeno relatório JSON fictício sobre vendas de carros." # Instruções do agente
)

# Agente 2: Tradutor/Formatador
tradutor = Agent( # Cria um agente
    name="Tradutor", # Nome do agente
    role="Tradutor Técnico", # Função do agente
    model=Groq(id="openai/gpt-oss-120b"), # Modelo do agente
    instructions="Receba dados técnicos e transforme em um parágrafo executivo em Português." # Instruções do agente
)

print("--- Passo 1: Analista gerando dados ---")
resposta_analista = analista.run("Gere dados de vendas de Janeiro/2025") # Executa o agente 1

print("\n--- Passo 2: Tradutor processando ---")
# Passamos a saída (content) do agente anterior como input
tradutor.print_response(f"Transforme isso em relatório: {resposta_analista.content}") # Executa o agente 2


