import sys
import pytest
from unittest.mock import patch


def test_parse_arguments_no_topic(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py"])
    from main import parse_arguments
    args = parse_arguments()
    assert args.topic is None


def test_parse_arguments_with_topic(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["main.py", "--topic", "quantum computing"])
    from main import parse_arguments
    args = parse_arguments()
    assert args.topic == "quantum computing"


def test_validate_keys_passes_when_both_present(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-anthropic-key")
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily-key")
    from main import validate_keys
    validate_keys()  # Should not raise


def test_validate_keys_exits_when_anthropic_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily-key")
    from main import validate_keys
    with pytest.raises(SystemExit) as exc_info:
        validate_keys()
    assert exc_info.value.code == 1


def test_validate_keys_exits_when_tavily_missing(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-anthropic-key")
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    from main import validate_keys
    with pytest.raises(SystemExit) as exc_info:
        validate_keys()
    assert exc_info.value.code == 1


def test_validate_keys_exits_when_both_missing(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    from main import validate_keys
    with pytest.raises(SystemExit) as exc_info:
        validate_keys()
    assert exc_info.value.code == 1


def test_print_result_outputs_text(capsys):
    from main import print_result
    print_result("Here is the answer.")
    captured = capsys.readouterr()
    assert "Here is the answer." in captured.out
    assert "RESEARCH RESULT" in captured.out
