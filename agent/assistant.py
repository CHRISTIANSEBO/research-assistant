from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_tool_calling_agent, AgentExecutor
from agent.tools import get_tools
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def create_research_agent():
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")
    tools = get_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert research assistant. Your job is to find accurate, up to date information and present it clearly.

Follow these rules for every response:
- Always search for information before answering
- Start with a short 2-3 sentence summary of the topic
- Present findings as clear bullet points
- Cite the source URL for each key finding
- Use a professional, educational tone
- If you are unsure about something, say so clearly
"""),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=False)
