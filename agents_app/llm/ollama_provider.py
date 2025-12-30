from agno.models.ollama import Ollama

def get_llm():
    return Ollama(
        model="mistral-small:latest",
        temperature=0.1,
        base_url="http://localhost:11434"
    )