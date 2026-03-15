from unittest.mock import patch, MagicMock


def test_get_tools_returns_list():
    mock_tool = MagicMock()
    with patch("agent.tools.TavilySearchResults", return_value=mock_tool):
        from agent.tools import get_tools
        tools = get_tools()
    assert isinstance(tools, list)


def test_get_tools_returns_one_tool():
    mock_tool = MagicMock()
    with patch("agent.tools.TavilySearchResults", return_value=mock_tool):
        from agent.tools import get_tools
        tools = get_tools()
    assert len(tools) == 1


def test_get_tools_uses_max_results_3():
    with patch("agent.tools.TavilySearchResults") as MockTavily:
        MockTavily.return_value = MagicMock()
        from agent.tools import get_tools
        get_tools()
    MockTavily.assert_called_once_with(max_results=3)
