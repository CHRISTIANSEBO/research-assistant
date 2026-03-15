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
    llm = ChatAnthropic(model="claude-sonnet-4")
    
    # Get our tools list from tools.py
    tools = get_tools()
    
    # Define the prompt — this tells Claude what its role is
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
    # This inserts the conversation history so the agent remembers context
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
    
    # Create the agent — this binds Claude, the tools, and the prompt together
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # AgentExecutor is the runtime — it actually runs the agent in a loop until done
    executor = AgentExecutor(agent=agent, tools=tools, verbose=False) 
    
    return executor
