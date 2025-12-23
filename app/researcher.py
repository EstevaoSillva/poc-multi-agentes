from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.duckduckgo import DuckDuckGoTools

model = Ollama(
    id="mistral:7b",
)

researcher_agent = Agent(
    name="Researcher Web",
    role="Especialista em pesquisa web",
    model=model,
    tools=[DuckDuckGoTools()],
    instructions=[
        "Você é um pesquisador web especializado em encontrar informações precisas e relevantes na internet.",
        "Seu trabalho é realizar pesquisas eficazes para responder às perguntas dos usuários.",
        "Utilize as ferramentas de pesquisa disponíveis para obter os melhores resultados.",
        "Forneça respostas claras e concisas com base nas informações encontradas."
    ],
)

