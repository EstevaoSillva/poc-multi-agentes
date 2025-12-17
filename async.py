import asyncio
from agno.agent import Agent
from agno.models.groq import Groq

from dotenv import load_dotenv

# Carrega as chaves do arquivo .env
load_dotenv()

# Definição dos agentes
agente_poesia = Agent(model=Groq(id="openai/gpt-oss-120b"), instructions="Escreva um poema curto.") # Cria um agente para escrever uma poema
agente_piada = Agent(model=Groq(id="openai/gpt-oss-120b"), instructions="Conte uma piada seca.") # Cria um agente para contar uma piada

async def executar_paralelo():
    print("--- Iniciando execução paralela ---")
    
    # Cria as tarefas para rodarem simultaneamente
    tarefa1 = agente_poesia.arun("Sobre inteligência artificial.") # Executa o agente 1 em paralelo
    tarefa2 = agente_piada.arun("Sobre programadores.") # Executa o agente 2 em paralelo
 
    # Aguarda ambas finalizarem (gather)
    respostas = await asyncio.gather(tarefa1, tarefa2) # Aguarda ambas finalizarem

    print(f"\nPOEMA:\n{respostas[0].content}") # Imprime a resposta do agente 1
    print(f"\nPIADA:\n{respostas[1].content}") # Imprime a resposta do agente 2

# Executa o loop assíncrono 
asyncio.run(executar_paralelo()) 