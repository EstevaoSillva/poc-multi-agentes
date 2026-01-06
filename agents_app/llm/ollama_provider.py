import os
from agno.models.ollama import Ollama

# Default model IDs (overridable via environment variables)
_CHAT_MODEL_ID = os.getenv("OLLAMA_CHAT_MODEL")
_CODE_MODEL_ID = os.getenv("OLLAMA_CODE_MODEL")
_FALLBACK_MODEL_ID = os.getenv("OLLAMA_FALLBACK_MODEL")


def get_chat_llm():
    """
    Chat / UX / Onboarding
    """
    return Ollama(
        id=_CHAT_MODEL_ID,
    )


def get_code_llm():
    """
    Code generation / architecture / planning
    """
    return Ollama(
        id=_CODE_MODEL_ID,
    )


def get_fallback_llm():
    """
    Fallback / structured output
    """
    return Ollama(
        id=_FALLBACK_MODEL_ID,
    )


def get_llm(model_type: str = "code"):
    """
    Smart LLM selector based on task type.
    
    Args:
        model_type: One of "chat", "code", "fallback", or "default"
                    - "chat": for conversational tasks (ideation, refinement)
                    - "code": for code generation and technical planning (default)
                    - "fallback": when primary models fail
                    - "default": alias for "code"
    
    Returns:
        Ollama instance configured for the specified task type
    
    Examples:
        # For agent that generates code
        generator_llm = get_llm("code")
        
        # For conversational ideation agent
        ideation_llm = get_llm("chat")
        
        # For robustness in fallback scenarios
        safe_llm = get_llm("fallback")
    """
    if model_type == "chat":
        return get_chat_llm()
    elif model_type == "fallback":
        return get_fallback_llm()
    elif model_type in ("code", "default", None):
        return get_code_llm()
    else:
        # Default to code LLM for unknown types
        return get_code_llm()