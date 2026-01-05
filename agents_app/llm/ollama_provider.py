from agno.models.ollama import Ollama

def get_llm():
    return Ollama(
        # id="deepseek-coder:6.7b",
        id="mistral-small:latest",
    )