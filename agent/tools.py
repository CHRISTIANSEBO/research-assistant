# Imports the Tavily search tool from LangChain's community tools
from langchain_community.tools.tavily_search import TavilySearchResults

def get_tools():
    # Creates a Tavily search tool that returns up to 3 results per search
    # LangChain automatically picks up TAVILY_API_KEY from .env
    search_tool = TavilySearchResults(max_results=3)
    
    # Return the tools as a list
    return [search_tool]
