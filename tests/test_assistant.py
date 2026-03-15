import sys
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture()
def mock_langchain(monkeypatch):
    """Patch heavy langchain imports so agent.assistant can be imported in tests."""
    mock_executor_cls = MagicMock()
    mock_executor_instance = MagicMock()
    mock_executor_cls.return_value = mock_executor_instance
    mock_executor_instance.__class__ = mock_executor_cls

    mock_agents = MagicMock()
    mock_agents.AgentExecutor = mock_executor_cls
    mock_agents.create_tool_calling_agent = MagicMock(return_value=MagicMock())

    monkeypatch.setitem(sys.modules, "langchain.agents", mock_agents)
    monkeypatch.setitem(sys.modules, "langchain_anthropic", MagicMock())
    monkeypatch.setitem(sys.modules, "langchain_core.prompts", MagicMock())
    monkeypatch.setitem(sys.modules, "dotenv", MagicMock())

    # Remove cached agent.assistant so it re-imports with mocks
    monkeypatch.delitem(sys.modules, "agent.assistant", raising=False)

    return mock_agents


def test_create_agent_calls_llm(mock_langchain):
    mock_anthropic = MagicMock(return_value=MagicMock())
    mock_langchain_anthropic = MagicMock()
    mock_langchain_anthropic.ChatAnthropic = mock_anthropic

    with patch.dict(sys.modules, {"langchain_anthropic": mock_langchain_anthropic}), \
         patch("agent.tools.get_tools", return_value=[MagicMock()]):
        import agent.assistant as assistant_mod
        agent_mod_anthropic = assistant_mod.ChatAnthropic
        with patch.object(assistant_mod, "ChatAnthropic", mock_anthropic), \
             patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
            assistant_mod.create_agent()
    mock_anthropic.assert_called_once_with(model="claude-sonnet-4")


def test_create_agent_uses_claude_sonnet(mock_langchain):
    with patch.dict(sys.modules, {}):
        import agent.assistant as assistant_mod
        mock_llm_cls = MagicMock(return_value=MagicMock())
        with patch.object(assistant_mod, "ChatAnthropic", mock_llm_cls), \
             patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
            assistant_mod.create_agent()
    mock_llm_cls.assert_called_once_with(model="claude-sonnet-4")


def test_create_agent_calls_get_tools(mock_langchain):
    import agent.assistant as assistant_mod
    mock_get_tools = MagicMock(return_value=[MagicMock()])
    with patch.object(assistant_mod, "ChatAnthropic", MagicMock(return_value=MagicMock())), \
         patch.object(assistant_mod, "get_tools", mock_get_tools):
        assistant_mod.create_agent()
    mock_get_tools.assert_called_once()


def test_create_agent_executor_verbose_false(mock_langchain):
    import agent.assistant as assistant_mod
    with patch.object(assistant_mod, "ChatAnthropic", MagicMock(return_value=MagicMock())), \
         patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
        assistant_mod.create_agent()
    _, kwargs = mock_langchain.AgentExecutor.call_args
    assert kwargs.get("verbose") is False
