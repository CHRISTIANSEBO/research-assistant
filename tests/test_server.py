from types import SimpleNamespace


def test_health_reports_build_and_effective_model(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-test-model")

    import server

    response = server.app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "build": "model-delete-v3",
        "anthropic_model": "claude-test-model",
    }


# ---------------------------------------------------------------------------
# _chunk_text: extracts plain text from a streamed chat-model chunk while
# skipping tool-call / non-text content blocks.
# ---------------------------------------------------------------------------

def test_chunk_text_returns_empty_when_content_missing():
    import server

    # A chunk object without a ``content`` attribute (getattr default -> None).
    assert server._chunk_text(object()) == ""


def test_chunk_text_returns_empty_when_content_is_none():
    import server

    assert server._chunk_text(SimpleNamespace(content=None)) == ""


def test_chunk_text_returns_string_content_directly():
    import server

    assert server._chunk_text(SimpleNamespace(content="hello world")) == "hello world"


def test_chunk_text_joins_text_blocks_and_skips_non_text():
    import server

    content = [
        {"type": "text", "text": "Hello "},
        {"type": "tool_use", "name": "search", "input": {}},  # skipped
        {"type": "text", "text": "world"},
        {"type": "text"},  # missing "text" -> treated as empty string
        "not-a-dict",  # skipped
    ]
    assert server._chunk_text(SimpleNamespace(content=content)) == "Hello world"


def test_chunk_text_returns_empty_for_unexpected_content_type():
    import server

    # content is neither str nor list (e.g. an int) -> empty string.
    assert server._chunk_text(SimpleNamespace(content=123)) == ""


# ---------------------------------------------------------------------------
# _extract_output: pulls the final answer string out of an AgentExecutor
# chain output, handling dict, list-of-blocks, and plain-string shapes.
# ---------------------------------------------------------------------------

def test_extract_output_from_dict_with_string_output():
    import server

    assert server._extract_output({"output": "the answer"}) == "the answer"


def test_extract_output_from_dict_with_list_output():
    import server

    out = {"output": [{"type": "text", "text": "part 1 "}, {"text": "part 2"}]}
    assert server._extract_output(out) == "part 1 part 2"


def test_extract_output_from_plain_list():
    import server

    out = [{"text": "a"}, {"text": "b"}, "skip-non-dict"]
    assert server._extract_output(out) == "ab"


def test_extract_output_from_plain_string():
    import server

    assert server._extract_output("just a string") == "just a string"


def test_extract_output_returns_empty_for_unexpected_type():
    import server

    # Neither dict, list, nor str (e.g. None) -> empty string.
    assert server._extract_output(None) == ""


def test_extract_output_dict_missing_output_key_returns_empty():
    import server

    assert server._extract_output({"other": "x"}) == ""
