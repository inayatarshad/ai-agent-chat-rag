# AI Agent Chat Interface 🤖🌿

An intelligent chatbot powered by LangGraph and RAG (Retrieval-Augmented Generation) that answers questions about LLM agents and prompt engineering.

## Features

- 🔍 **Semantic Search** over blog posts
- 🤖 **AI-Powered** query understanding
- 📝 **Automatic Query Rewriting** for better results
- 💬 **Context-Aware** responses
- ⚡ **Powered by Groq** for fast inference
- 🌿 **Beautiful Forest-Neon UI**

## Tech Stack

- **Frontend:** Streamlit
- **AI Framework:** LangChain, LangGraph
- **LLM:** Groq (Llama 3.3 70B)
- **Embeddings:** HuggingFace (all-MiniLM-L6-v2)
- **Vector Store:** ChromaDB

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

2. **Create a virtual environment:**
```bash
python -m venv .venv

# Activate it:
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
   -make .env file
   - Fill in your API keys:
     - Get Groq API key from: https://console.groq.com
     - Get LangChain API key from: https://smith.langchain.com
     - Get Tavily API key from: https://tavily.com
```bash


5. **Run the app:**
```bash
streamlit run app.py
```

## Project Structure
```
.
├── app.py              # Main Streamlit application
├── agent_graph.py      # LangGraph agent logic
├── .env       # Environment variables template
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## API Keys Required

- **GROQ_API_KEY**: Free tier available at [Groq Console](https://console.groq.com)
- **LANGCHAIN_API_KEY**: For LangSmith tracing (optional)
- **TAVILY_API_KEY**: For web search capabilities (optional)

## Usage

1. Start the app with `streamlit run app.py`
2. Ask questions about:
   - LLM agents
   - Prompt engineering
   - Autonomous agents
   - Memory systems in AI
   - And more!

## Screenshots
![Screenshot 1](imgs\pic1.png)
<!-- Add screenshots here later -->

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License

## Acknowledgments

- Blog posts by [Lilian Weng](https://lilianweng.github.io/)
- Powered by [LangChain](https://langchain.com/) and [Groq](https://groq.com/)