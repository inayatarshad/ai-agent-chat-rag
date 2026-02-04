import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_core.messages import HumanMessage

# Import the compiled agent
from agent_graph import app as agent_app

st.set_page_config(
    page_title="AI Agent Chat Interface", 
    page_icon="🤖",
    layout="wide"
)

# Custom CSS - Forest Green + Neon Theme
st.markdown("""
    <style>
    /* Main background - Dark forest green gradient */
    .stApp {
        background: linear-gradient(135deg, #0a1f1f 0%, #134e4a 50%, #065f46 100%);
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: rgba(16, 185, 129, 0.1);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    
    /* User messages - Neon green accent */
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
        border-left: 3px solid #10b981;
        background-color: rgba(16, 185, 129, 0.15);
    }
    
    /* Assistant messages - Neon cyan accent */
    [data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
        border-left: 3px solid #06b6d4;
        background-color: rgba(6, 182, 212, 0.15);
    }
    
    /* Sidebar - Deep forest */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #064e3b 0%, #022c22 100%);
        border-right: 2px solid rgba(16, 185, 129, 0.3);
    }
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #10b981;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    
    /* Button styling - Neon green */
    .stButton>button {
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        color: #ffffff;
        border-radius: 25px;
        border: 2px solid #10b981;
        padding: 12px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #059669 0%, #047857 100%);
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.8);
        border-color: #34d399;
    }
    
    /* Chat input - Neon border */
    .stChatInputContainer {
        background-color: rgba(6, 78, 59, 0.5);
        border-radius: 25px;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    
    .stChatInputContainer:focus-within {
        border-color: #10b981;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.5);
    }
    
    /* Title - Neon glow effect */
    h1 {
        color: #10b981;
        text-align: center;
        font-size: 2.8em;
        text-shadow: 
            0 0 10px rgba(16, 185, 129, 0.8),
            0 0 20px rgba(16, 185, 129, 0.6),
            0 0 30px rgba(16, 185, 129, 0.4);
        padding: 20px;
        font-weight: 800;
        letter-spacing: 2px;
    }
    
    /* Spinner - Green */
    .stSpinner > div {
        border-top-color: #10b981 !important;
    }
    
    /* Info boxes - Forest theme */
    .stInfo {
        background-color: rgba(6, 78, 59, 0.3);
        border-left: 4px solid #10b981;
        color: #d1fae5;
    }
    
    /* Text colors */
    p, span, label {
        color: #d1fae5;
    }
    
    /* Markdown in sidebar */
    [data-testid="stSidebar"] .element-container div[data-testid="stMarkdownContainer"] p {
        color: #a7f3d0;
    }
    
    [data-testid="stSidebar"] .element-container div[data-testid="stMarkdownContainer"] li {
        color: #d1fae5;
    }
    
    /* Error messages - Red neon */
    .stError {
        background-color: rgba(127, 29, 29, 0.3);
        border-left: 4px solid #ef4444;
        color: #fecaca;
    }
    
    /* Success/warning - Adjusted for theme */
    .stSuccess {
        background-color: rgba(6, 78, 59, 0.4);
        border-left: 4px solid #10b981;
        color: #d1fae5;
    }
    
    /* Scrollbar - Neon green */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #064e3b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #34d399 0%, #10b981 100%);
    }
    
    /* Avatar icons - Neon glow */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.6);
    }
    
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.6);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌿 AI Agent Chat Interface 🤖")

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("🌱 Enter your query...")

if user_input:
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.chat_message("user"):
        st.write(user_input)
    
    with st.chat_message("assistant"):
        with st.spinner("🔮 Processing your query..."):
            try:
                # Invoke the agent
                result = agent_app.invoke({"messages": [HumanMessage(content=user_input)]})
                
                # Extract the final response
                if result and "messages" in result:
                    final_message = result["messages"][-1]
                    response_text = final_message.content if hasattr(final_message, 'content') else str(final_message)
                else:
                    response_text = "I apologize, but I couldn't generate a response."
                
                st.write(response_text)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                error_message = f"Error processing query: {str(e)}"
                st.error(error_message)
                st.session_state.chat_history.append({"role": "assistant", "content": error_message})

# Sidebar
with st.sidebar:
    st.markdown("### 🌲 About")
    st.info("This Streamlit app interacts with an AI agent powered by LangGraph to answer queries using RAG (Retrieval-Augmented Generation).")
    
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🔍 Semantic search over blog posts
    - 🤖 AI-powered query understanding
    - 📝 Automatic query rewriting for better results
    - 💬 Context-aware responses
    """)
    
    st.markdown("---")
    
    # Add a clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("🌿 Made with **Forest Energy** 🌿")