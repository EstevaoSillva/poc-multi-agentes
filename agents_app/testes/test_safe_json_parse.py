from agents_app.utils import safe_json_parse


def test_json_inside_markdown():
    text = """```json
    {"a": 1}
    ```"""
    assert safe_json_parse(text) == {"a": 1}
