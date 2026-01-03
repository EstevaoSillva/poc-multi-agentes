from agno.models.ollama import Ollama

def get_llm():
    return Ollama(
        id="mistral-small:latest",
    )