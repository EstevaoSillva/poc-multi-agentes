import json
import re


def str_to_bool(value: str) -> bool:
    return value.strip().lower() in ('1', 'yes', 'true', 't')


def extract_json(text: str) -> dict:
    """
    Extrai JSON mesmo que venha envolvido em ```json ... ```
    """
    # Remove ```json e ```
    cleaned = re.sub(r"```(?:json)?", "", text).strip()

    return json.loads(cleaned)