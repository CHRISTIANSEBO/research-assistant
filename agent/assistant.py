# Load environment variables from .env
from dotenv import load_dotenv

# Import the Claude LLM via LangChain
from langchain_anthropic import ChatAnthropic

# Import the function that creates our agent
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Import the tools we defined in tools.py
from agent.tools import get_tools

# Import prompt template — this structures how we talk to the agent
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

def create_agent():
    # Initialize Claude as our LLM
    llm = ChatAnthropic(model="claude-sonnet-4-20250514")
    
    # Get our tools list from tools.py
    tools = get_tools()
    
    # Define the prompt — this tells Claude what its role is
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful research assistant. Use the search tool to find accurate and up to date information."),
        ("human", "{input}"),
        # This is required — it's where the agent stores its reasoning steps
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent — this binds Claude, the tools, and the prompt together
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # AgentExecutor is the runtime — it actually runs the agent in a loop until done
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return executor
