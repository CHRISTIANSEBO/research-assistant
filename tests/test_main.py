import sys
import pytest
from unittest.mock import MagicMock, patch


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


def test_main_survives_agent_error(monkeypatch, capsys):
    """Regression: an agent failure must not crash the REPL with UnboundLocalError.

    Previously the loop appended ``AIMessage(content=output)`` unconditionally
    after the try/except, so when ``agent.invoke`` raised (before ``output`` was
    ever assigned) the next line blew up with UnboundLocalError instead of
    letting the user retry.
    """
    import main

    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-anthropic-key")
    monkeypatch.setenv("TAVILY_API_KEY", "fake-tavily-key")
    monkeypatch.setattr(sys, "argv", ["main.py"])

    failing_agent = MagicMock()
    failing_agent.invoke.side_effect = RuntimeError("boom")
    monkeypatch.setattr(main, "create_research_agent", lambda: failing_agent)

    # First a real query (which triggers the failing agent), then "exit".
    monkeypatch.setattr("builtins.input", MagicMock(side_effect=["tell me about x", "exit"]))

    # Must return cleanly rather than raising UnboundLocalError.
    main.main()

    captured = capsys.readouterr()
    assert "Something went wrong" in captured.out
    assert "boom" in captured.out
    # The failed exchange should be reported and skipped without a crash.
    failing_agent.invoke.assert_called_once()
