import warnings
warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
load_dotenv()

from typing import Annotated, Literal, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import create_retriever_tool
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langgraph.prebuilt import tools_condition
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

# Environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY if TAVILY_API_KEY else ""
os.environ["GROQ_API_KEY"] = GROQ_API_KEY if GROQ_API_KEY else ""
os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY if LANGCHAIN_API_KEY else ""
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Setup embeddings and LLM
from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

from langchain_groq import ChatGroq
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

# Load documents
urls = [
    "https://lilianweng.github.io/posts/2023-06-23-agent/",
    "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
]

print("Loading documents...")
docs = [WebBaseLoader(url).load() for url in urls]
docs_list = [item for sublist in docs for item in sublist]

# Split documents
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=100, chunk_overlap=5
)
doc_splits = text_splitter.split_documents(docs_list)

# Create vectorstore
print("Creating vectorstore...")
vectorstore = Chroma.from_documents(
    documents=doc_splits,
    collection_name="rag-chrome",
    embedding=embeddings
)
retriever = vectorstore.as_retriever()

# Create retriever tool
retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_blog_posts",
    "Search and return information about Lilian Weng blog posts on LLM agents, prompt engineering, and adversarial attacks on LLMs."
)

tools = [retriever_tool]
retrieve = ToolNode([retriever_tool])

# Define state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]

# Define nodes with better logic
def ai_assistant(state: AgentState):
    print("---CALL AGENT---")
    messages = state['messages']
    user_message = messages[0].content if messages else ""
    
    # Simple queries that don't need retrieval
    simple_queries = ["hi", "hello", "how are you", "what are you", "who are you", "thanks", "thank you", "useful"]
    
    # Check if it's a simple query
    if any(query in user_message.lower() for query in simple_queries) and len(user_message.split()) < 10:
        print("---SIMPLE QUERY: DIRECT RESPONSE---")
        response = llm.invoke([HumanMessage(content=user_message)])
        return {"messages": [response]}
    
    # Blog-related keywords
    blog_keywords = ["agent", "llm", "prompt", "engineering", "adversarial", "attack", "autonomous", "memory", "planning", "tool", "rag"]
    is_blog_query = any(keyword in user_message.lower() for keyword in blog_keywords)
    
    if is_blog_query:
        print("---BLOG QUERY: USING TOOLS---")
        llm_with_tool = llm.bind_tools(tools, tool_choice="auto")
        response = llm_with_tool.invoke(messages)
        return {"messages": [response]}
    else:
        print("---GENERAL QUERY: DIRECT RESPONSE---")
        response = llm.invoke(messages)
        return {"messages": [response]}

class grade(BaseModel):
    binary_score: str = Field(description="Relevance score 'yes' or 'no'")

def grade_documents(state: AgentState) -> Literal["generator", "rewriter"]:
    llm_with_structure_op = llm.with_structured_output(grade)
    
    prompt = PromptTemplate(
        template="""You are a grader deciding if a document is relevant to a user's question.
        
        Here is the document:
        {context}
        
        Here is the user's question: {question}
        
        If the document talks about or contains information related to the user's question, mark it as relevant.
        Give a 'yes' or 'no' answer to show if the document is relevant to the question.""",
        input_variables=["context", "question"]
    )
    
    chain = prompt | llm_with_structure_op
    messages = state["messages"]
    last_message = messages[-1]
    question = messages[0].content
    docs = last_message.content
    
    scored_result = chain.invoke({"question": question, "context": docs})
    score = scored_result.binary_score
    
    if score == "yes":
        print("---DECISION: DOCS RELEVANT---")
        return "generator"
    else:
        print("---DECISION: DOCS NOT RELEVANT---")
        return "rewriter"

def generate(state: AgentState):
    print("---GENERATE---")
    messages = state["messages"]
    question = messages[0].content
    last_message = messages[-1]
    docs = last_message.content
    
    rag_prompt = PromptTemplate(
        template="""You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.

Question: {question}

Context: {context}

Answer:""",
        input_variables=["question", "context"]
    )
    
    rag_chain = rag_prompt | llm
    response = rag_chain.invoke({"context": docs, "question": question})
    
    return {"messages": [response]}

def rewrite(state: AgentState):
    print("---TRANSFORM QUERY---")
    messages = state["messages"]
    question = messages[0].content
    
    message = [HumanMessage(
        content=f"""Look at the input and try to reason about the underlying semantic intent or meaning.
        
        Here is the initial question: {question}
        Formulate an improved question:"""
    )]
    
    response = llm.invoke(message)
    return {"messages": [response]}

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("My_AI_Assistant", ai_assistant)
workflow.add_node("Vector_Retriever", retrieve)
workflow.add_node("Query_Rewriter", rewrite)
workflow.add_node("Output_Generator", generate)

workflow.add_edge(START, "My_AI_Assistant")
workflow.add_conditional_edges(
    "My_AI_Assistant",
    tools_condition,
    {"tools": "Vector_Retriever", END: END}
)
workflow.add_conditional_edges(
    "Vector_Retriever",
    grade_documents,
    {"generator": "Output_Generator", "rewriter": "Query_Rewriter"}
)
workflow.add_edge("Output_Generator", END)
workflow.add_edge("Query_Rewriter", "My_AI_Assistant")

# Compile the app
app = workflow.compile()
print("Agent graph compiled successfully!")