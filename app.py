import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from agent.assistant import create_research_agent
from agent.file_handler import save_research
import os

load_dotenv()

st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔍",
    layout="centered",
)

st.markdown("""
<style>
/* Base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #ffffff;
    color: #1a1a1a;
}

[data-testid="stHeader"]  { background-color: #ffffff; }
[data-testid="stBottom"]  { background-color: #ffffff; }

#MainMenu, footer { visibility: hidden; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background-color: #f4f4f4;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 8px;
    border: none;
}

/* Input bar */
[data-testid="stChatInput"] textarea {
    background-color: #f4f4f4 !important;
    color: #1a1a1a !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 24px !important;
    font-size: 1rem !important;
}

[data-testid="stChatInput"] textarea:focus {
    border-color: #bbb !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}

/* Bottom bar — force white */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
section[data-testid="stBottom"] {
    background-color: #ffffff !important;
    border-top: 1px solid #f0f0f0 !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #f9f9f9;
    border-right: 1px solid #ebebeb;
}

/* Suggestion chips */
.chip-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 24px;
}

.chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 999px;
    border: 1px solid #e0e0e0;
    background: #ffffff;
    color: #1a1a1a;
    font-size: 0.875rem;
    cursor: pointer;
    transition: background 0.15s;
    white-space: nowrap;
}

.chip:hover { background: #f4f4f4; }

/* Sidebar buttons */
.stButton > button {
    background-color: #f4f4f4;
    color: #1a1a1a;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    width: 100%;
    text-align: left;
    padding: 6px 12px;
    font-size: 0.85rem;
}

.stButton > button:hover {
    background-color: #ebebeb;
    border-color: #ccc;
}

/* Landing heading */
.landing-title {
    text-align: center;
    font-size: 4rem;
    font-weight: 600;
    color: #1a1a1a;
    margin-bottom: 0;
}

/* Headers — force black everywhere including inside chat bubbles */
h1, h2, h3, h4, h5, h6 { color: #1a1a1a !important; }
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4 { color: #1a1a1a !important; }
p, li { color: #333; }
</style>
""", unsafe_allow_html=True)


# Session state
if "agent" not in st.session_state:
    st.session_state.agent = create_research_agent()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "saved_files" not in st.session_state:
    st.session_state.saved_files = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "conversations" not in st.session_state:
    st.session_state.conversations = []  # list of {title, messages, chat_history}

if "load_conversation" not in st.session_state:
    st.session_state.load_conversation = None


def archive_current_conversation():
    """Save the current conversation to history before clearing it."""
    if st.session_state.messages:
        first_user_msg = next(
            (m["content"] for m in st.session_state.messages if m["role"] == "user"), None
        )
        title = (first_user_msg[:45] + "...") if first_user_msg and len(first_user_msg) > 45 else first_user_msg
        st.session_state.conversations.insert(0, {
            "title": title or "Conversation",
            "messages": list(st.session_state.messages),
            "chat_history": list(st.session_state.chat_history),
        })


# Sidebar
with st.sidebar:
    st.markdown("<p style='text-align:left; font-size:1.5rem; font-weight:600; color:#1a1a1a; line-height:1.2;'>Research Assistant</p>", unsafe_allow_html=True)
    st.markdown("<small style='color:#888'>Powered by Claude + Tavily</small>", unsafe_allow_html=True)
    st.divider()

    if st.button("+ New conversation", use_container_width=True):
        archive_current_conversation()
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.session_state.pending_query = None
        st.rerun()

    if st.session_state.conversations:
        st.markdown("<small style='color:#999; text-transform:uppercase; letter-spacing:0.05em'>Previous conversations</small>", unsafe_allow_html=True)
        for i, convo in enumerate(st.session_state.conversations):
            if st.button(convo["title"], key=f"convo_{i}", use_container_width=True):
                st.session_state.load_conversation = i
                st.rerun()

    st.divider()
    st.markdown("<small style='color:#bbb'>Results are auto-saved to results/</small>", unsafe_allow_html=True)


# Load a previous conversation
if st.session_state.load_conversation is not None:
    idx = st.session_state.load_conversation
    convo = st.session_state.conversations[idx]
    st.session_state.messages = list(convo["messages"])
    st.session_state.chat_history = list(convo["chat_history"])
    st.session_state.load_conversation = None
    st.rerun()


# Landing view (no messages yet)
SUGGESTIONS = [
    ("Find recent news on...", "Find recent news on artificial intelligence"),
    ("Summarize a topic", "Give me a summary of quantum computing"),
    ("Compare two things", "Compare Python vs JavaScript for backend development"),
]

if not st.session_state.messages:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; font-size:2rem; font-weight:600; color:#1a1a1a; line-height:1.2;'>What can I research for you?</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    for col, (label, query) in zip([col1, col2, col3], SUGGESTIONS):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.pending_query = query
                st.rerun()

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)

else:
    # Chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


# Process pending query from suggestion chips
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
else:
    query = None


# Chat input
typed_query = st.chat_input("Ask a research question...")
if typed_query:
    query = typed_query

if query:
    if not os.getenv("ANTHROPIC_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        st.error("Missing API keys. Add ANTHROPIC_API_KEY and TAVILY_API_KEY to your .env file.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                response = st.session_state.agent.invoke({
                    "input": query,
                    "chat_history": st.session_state.chat_history,
                })

                output = response["output"]
                if isinstance(output, list):
                    output = output[0].get("text", "")

                st.markdown(output)

                filename = save_research(query, output)
                st.session_state.saved_files.append(filename)
                st.caption(f"Saved to {filename}")

                st.session_state.messages.append({"role": "assistant", "content": output})
                st.session_state.chat_history.append(HumanMessage(content=query))
                st.session_state.chat_history.append(AIMessage(content=output))

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")
