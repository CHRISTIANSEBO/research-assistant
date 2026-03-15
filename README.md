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
- **UI:** Streamlit
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

5. Run the web app
```bash
   streamlit run app.py
```

Or run the CLI version
```bash
   python main.py
```

## 📁 Project Structure
```
research-assistant/
├── .env
├── .gitignore
├── requirements.txt
├── app.py
├── main.py
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
- Clean, responsive web interface built with Streamlit
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
