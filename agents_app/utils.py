import json
import re


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ('1', 'yes', 'true', 't')


def safe_json_parse(text: str) -> dict:
    if not text:
        raise ValueError("LLM returned empty response")

    # 1. Tenta extrair blocos de código markdown primeiro (é o mais comum)
    code_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    for block in code_blocks:
        try:
            return json.loads(block.strip())
        except json.JSONDecodeError:
            continue

    # 2. Se não houver blocos, tenta encontrar o maior objeto JSON possível na string
    # Isso resolve o problema de "Extra data" (texto após o JSON)
    start_index = text.find('{')
    end_index = text.rfind('}')

    if start_index != -1 and end_index != -1:
        # Tentativa iterativa: se houver texto extra, tentamos reduzir do fim para o início
        # para encontrar o fechamento correto caso existam múltiplas chaves
        candidate = text[start_index:end_index + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # Se falhou, pode ser que o rfind pegou o } de um texto explicativo
            # Vamos tentar o parsing padrão do regex abaixo
            pass

    # 3. Fallback: Procura por algo que se pareça com um objeto JSON usando regex
    # e tenta dar load. Útil se o modelo for muito verboso.
    try:
        # Encontra o primeiro { e o último } e ignora o resto
        match = re.search(r'(\{[\s\S]*\})', text)
        if match:
            return json.loads(match.group(1))
    except json.JSONDecodeError:
        pass

    # Caso especial: O modelo não seguiu o formato JSON mas enviou arquivos em markdown


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