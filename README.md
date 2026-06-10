# 🔍 AI Research Assistant

![Tests](https://github.com/CHRISTIANSEBO/research-assistant/actions/workflows/tests.yml/badge.svg)

An AI-powered research assistant that searches the web and delivers
clear, sourced answers through a chat interface.

## Screenshots

| Landing | Chat | Sidebar |
|---|---|---|
| ![Landing](demo_screenshots/demo1.png) | ![Chat](demo_screenshots/demo2.png) | ![Sidebar](demo_screenshots/demo3.png) |

## 🌍 The Problem
Finding reliable, up-to-date information online is time consuming.
Search engines return dozens of links that still require manual reading
and synthesis. There is no easy way to have a focused research
conversation that remembers context and saves results.

## 💡 The Solution
This agent accepts natural language research questions, searches the web
in real time, synthesizes findings into clear bullet points with sources,
remembers conversation context, and saves every result to a timestamped file.

## 🛠 Tech Stack
- **LLM:** Anthropic Claude (claude-sonnet)
- **Agent Framework:** LangChain
- **Search Tool:** Tavily API
- **Backend:** Flask (served with gunicorn)
- **Frontend:** Custom HTML / CSS / JavaScript (no framework)
- **Legacy UI:** Streamlit (`app.py`, still available)
- **Deployment:** Railway
- **Language:** Python 3.11

## ⚙️ Setup Instructions

1. Clone the repository
 ```bash
   git clone https://github.com/CHRISTIANSEBO/research-assistant.git
   cd research-assistant
```

2. Create and activate a virtual environment
```bash
   python -m venv venv
   venv\Scripts\activate
```

3. Install dependencies
```bash
   pip install -r requirements.txt
```

4. Add your API keys — create a .env file in the root folder
```
   ANTHROPIC_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
```

5. Run the web app (custom HTML/CSS/JS frontend on port 8080)
```bash
   python server.py
```
Then open http://localhost:8080

Or run the legacy Streamlit UI
```bash
   streamlit run app.py
```

Or run the CLI version
```bash
   python main.py
```

## 🚀 Deploying to Railway
The app is configured to run on Railway out of the box:
- `server.py` binds to `0.0.0.0` on `$PORT` (defaults to **8080**).
- `Procfile` / `railway.json` start the app with gunicorn and expose a `/health` check.

Steps:
1. Create a new Railway project from this repo.
2. Add the `ANTHROPIC_API_KEY` and `TAVILY_API_KEY` environment variables.
3. Railway builds with Nixpacks, installs `requirements.txt`, and starts:
   `gunicorn server:app --bind 0.0.0.0:$PORT`
4. Live at your Railway domain, e.g. `https://research-assistant-production-0.up.railway.app`

## 📁 Project Structure
```
research-assistant/
├── .env
├── .gitignore
├── requirements.txt
├── Procfile              # Railway / gunicorn start command
├── railway.json          # Railway deploy config
├── server.py             # Flask backend + JSON API (port 8080)
├── app.py                # Legacy Streamlit UI
├── main.py               # CLI
├── static/               # Custom HTML/CSS/JS frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
├── agent/
│   ├── __init__.py
│   ├── tools.py
│   ├── assistant.py
│   └── file_handler.py
└── tests/
    ├── test_file_handler.py
    ├── test_tools.py
    ├── test_assistant.py
    └── test_main.py
```


## 🧪 Running Tests
```bash
python -m pytest tests/ -v
```

## ✨ Features
- Clean, responsive web interface built with custom HTML/CSS/JS (Streamlit UI also available)
- ChatGPT-style layout: landing suggestions, chat view, and a conversation sidebar
- Conversation history persisted in the browser via localStorage
- Conversational memory across the session
- Real-time web search with cited sources
- Auto-saves research results to timestamped files in `results/research_YYYYMMDD_HHMMSS.txt`
- CLI interface also available via `python main.py`
- Error handling for API failures and missing keys
- Unit test suite covering all core modules

## Future Improvements
- Support for multiple search tools
- Export results to PDF or DOCX
- Multi-agent collaboration
