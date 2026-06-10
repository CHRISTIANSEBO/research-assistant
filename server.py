import asyncio
import json
import os

from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    jsonify,
    request,
    send_from_directory,
    stream_with_context,
)
from langchain_core.messages import AIMessage, HumanMessage

from agent.assistant import create_research_agent
from agent.file_handler import save_research


def _chunk_text(chunk):
    """Extract plain text from a streamed chat-model chunk, skipping tool calls."""
    content = getattr(chunk, "content", None)
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "".join(parts)
    return ""


def _extract_output(out):
    """Pull the final answer string out of an AgentExecutor chain output."""
    if isinstance(out, dict):
        out = out.get("output", "")
    if isinstance(out, list):
        return "".join(b.get("text", "") for b in out if isinstance(b, dict))
    return out if isinstance(out, str) else ""

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


# Bump on each frontend/behavior change so you can confirm what Railway is serving.
BUILD = "mobile-v2"


@app.route("/health")
def health():
    """Simple health check for Railway (also reports the running build)."""
    return jsonify({"status": "ok", "build": BUILD})


@app.after_request
def no_cache_assets(resp):
    """Force browsers to revalidate HTML/CSS/JS so new deploys are picked up."""
    if request.path == "/" or request.path.endswith((".html", ".css", ".js")):
        resp.headers["Cache-Control"] = "no-cache"
    return resp


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

    def event_stream():
        """Stream the agent's real steps and answer tokens as Server-Sent Events."""
        def sse(obj):
            return f"data: {json.dumps(obj)}\n\n"

        # Padding comment + early flush to defeat proxy/Railway response buffering.
        yield ":" + (" " * 2048) + "\n\n"
        yield "retry: 3000\n\n"

        agent = get_agent()
        answer_parts = []
        final_output = ""

        # astream_events is async; drive it from a private event loop so this
        # works inside Flask's synchronous (gunicorn) worker.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def run():
            nonlocal final_output
            async for ev in agent.astream_events(
                {"input": query, "chat_history": chat_history},
                version="v2",
            ):
                kind = ev.get("event")
                if kind == "on_tool_start":
                    tool_in = ev.get("data", {}).get("input", {})
                    q = tool_in.get("query") if isinstance(tool_in, dict) else tool_in
                    yield {"type": "step", "phase": "search",
                           "label": "Searching the web", "detail": str(q or "")}
                elif kind == "on_tool_end":
                    out = ev.get("data", {}).get("output")
                    count = len(out) if isinstance(out, list) else None
                    yield {"type": "step", "phase": "read", "label": "Read sources",
                           "detail": (f"{count} results" if count is not None else "")}
                elif kind == "on_chat_model_stream":
                    text = _chunk_text(ev.get("data", {}).get("chunk"))
                    if text:
                        answer_parts.append(text)
                        yield {"type": "token", "text": text}
                elif kind == "on_chain_end" and ev.get("name") == "AgentExecutor":
                    final_output = _extract_output(ev.get("data", {}).get("output"))

        agen = run().__aiter__()
        try:
            while True:
                try:
                    item = loop.run_until_complete(agen.__anext__())
                except StopAsyncIteration:
                    break
                yield sse(item)

            answer = "".join(answer_parts).strip() or final_output.strip()
            if answer and not answer_parts:
                # Streaming produced no text deltas; deliver the final answer at once.
                yield sse({"type": "token", "text": answer})

            saved_to = None
            if answer:
                try:
                    saved_to = save_research(query, answer)
                except Exception:  # noqa: BLE001 - saving is best-effort
                    saved_to = None

            yield sse({"type": "done", "saved_to": saved_to})
        except Exception as e:  # noqa: BLE001 - surface any agent/API error
            yield sse({"type": "error", "error": f"Something went wrong: {str(e)}"})
        finally:
            loop.close()

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(event_stream()), headers=headers)


if __name__ == "__main__":
    # Railway provides the port via $PORT; default to 8080 locally.
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
