import json
import re


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ('1', 'yes', 'true', 't')


def safe_json_parse(text: str) -> dict:
    if not text:
        raise ValueError("LLM returned empty response")

    # Remove blocos de código markdown se existirem
    cleaned = re.sub(r"```(?:json)?\n?([\s\S]*?)\n?```", r"\1", text).strip()

    # Se ainda houver sujeira fora do JSON, pegamos apenas o que está entre as primeiras e últimas chaves
    start_index = cleaned.find('{')
    end_index = cleaned.rfind('}')

    if start_index != -1 and end_index != -1:
        cleaned = cleaned[start_index:end_index + 1]

    # Caso não haja blocos de código, mas ainda haja sujeira ao redor
    if not cleaned.startswith('{') and '{' in cleaned:
        cleaned = cleaned[cleaned.find('{'):cleaned.rfind('}') + 1]

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Fallback ou log mais detalhado para debug
        raise ValueError(f"Failed to parse JSON: {e}. Raw text: {text}")


def extract_text_from_run(run_output) -> str:
    """
    Normaliza qualquer saída de agente para texto bruto
    """
    if hasattr(run_output, "content") and run_output.content:
        return run_output.content

    if hasattr(run_output, "output"):
        return run_output.output

    if hasattr(run_output, "messages") and run_output.messages:
        return "\n".join(
            m.get("content", "") for m in run_output.messages if isinstance(m, dict)
        )

    return str(run_output)