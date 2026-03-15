import sys
import pytest
from unittest.mock import MagicMock, patch

    # Test the create_research_agent function to ensure it sets up the agent correctly
@pytest.fixture()
def mock_langchain(monkeypatch):
    """Patch heavy langchain imports so agent.assistant can be imported in tests."""
    mock_executor_cls = MagicMock()
    mock_executor_cls.return_value = MagicMock()

    mock_agents = MagicMock()
    mock_agents.AgentExecutor = mock_executor_cls
    mock_agents.create_tool_calling_agent = MagicMock(return_value=MagicMock())

    monkeypatch.setitem(sys.modules, "langchain.agents", mock_agents)
    monkeypatch.setitem(sys.modules, "langchain_anthropic", MagicMock())
    monkeypatch.setitem(sys.modules, "langchain_core.prompts", MagicMock())
    monkeypatch.setitem(sys.modules, "dotenv", MagicMock())
    monkeypatch.delitem(sys.modules, "agent.assistant", raising=False)

    return mock_agents

    # Ensure the correct model is used when creating the research agent
def test_create_research_agent_uses_claude_sonnet(mock_langchain):
    import agent.assistant as assistant_mod
    mock_llm_cls = MagicMock(return_value=MagicMock())
    with patch.object(assistant_mod, "ChatAnthropic", mock_llm_cls), \
         patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
        assistant_mod.create_research_agent()
    mock_llm_cls.assert_called_once_with(model="claude-sonnet-4-20250514")

    # Ensure the LLM instance is passed to the agent
def test_create_research_agent_calls_get_tools(mock_langchain):
    import agent.assistant as assistant_mod
    mock_get_tools = MagicMock(return_value=[MagicMock()])
    with patch.object(assistant_mod, "ChatAnthropic", MagicMock(return_value=MagicMock())), \
         patch.object(assistant_mod, "get_tools", mock_get_tools):
        assistant_mod.create_research_agent()
    mock_get_tools.assert_called_once()

    # Ensure the tools are passed to the agent
def test_create_research_agent_executor_verbose_false(mock_langchain):
    import agent.assistant as assistant_mod
    with patch.object(assistant_mod, "ChatAnthropic", MagicMock(return_value=MagicMock())), \
         patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
        assistant_mod.create_research_agent()
    _, kwargs = mock_langchain.AgentExecutor.call_args
    assert kwargs.get("verbose") is False

    # Ensure the agent is created with verbose=False
def test_create_research_agent_returns_executor(mock_langchain):
    import agent.assistant as assistant_mod
    with patch.object(assistant_mod, "ChatAnthropic", MagicMock(return_value=MagicMock())), \
         patch.object(assistant_mod, "get_tools", return_value=[MagicMock()]):
        result = assistant_mod.create_research_agent()
    assert result is mock_langchain.AgentExecutor.return_value
