from agents_app.utils import extract_text_from_run


class FakeRun:
    content = '{"ok": true}'

def test_extract_text():
    run = FakeRun()
    assert extract_text_from_run(run) == '{"ok": true}'
