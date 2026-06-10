import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from langchain_core.messages import AIMessage, HumanMessage

from agent.assistant import create_research_agent
from agent.file_handler import save_research

load_dotenv()

# Serve the static front end (HTML/CSS/JS) from the ./static folder.
app = Flask(__name__, static_folder="static", static_url_path="")

# Build the agent once at startup and reuse it across requests.
_agent = None


def get_agent():
    """Lazily create the research agent so the server can boot without keys."""
    global _agent
    if _agent is None:
        _agent = create_research_agent()
    return _agent


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health")
def health():
    """Simple health check for Railway."""
    return jsonify({"status": "ok"})


@app.route("/api/research", methods=["POST"])
def research():
    data = request.get_json(silent=True) or {}
    query = (data.get("query") or "").strip()
    history = data.get("history") or []

    if not query:
        return jsonify({"error": "Please enter a research question."}), 400

    if not os.getenv("ANTHROPIC_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        return jsonify({
            "error": "Missing API keys. Set ANTHROPIC_API_KEY and TAVILY_API_KEY."
        }), 500

    # Rebuild LangChain chat history from the messages sent by the browser.
    chat_history = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "user":
            chat_history.append(HumanMessage(content=content))
        elif role == "assistant":
            chat_history.append(AIMessage(content=content))

    try:
        response = get_agent().invoke({
            "input": query,
            "chat_history": chat_history,
        })

        output = response["output"]
        if isinstance(output, list):
            output = output[0].get("text", "")

        filename = save_research(query, output)

        return jsonify({"answer": output, "saved_to": filename})

    except Exception as e:  # noqa: BLE001 - surface any agent/API error to the client
        return jsonify({"error": f"Something went wrong: {str(e)}"}), 500


if __name__ == "__main__":
    # Railway provides the port via $PORT; default to 8080 locally.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
