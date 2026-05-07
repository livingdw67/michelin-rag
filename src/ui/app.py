import streamlit as st
import os
import sys
from dotenv import load_dotenv

# Ensure Python can find our src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.engine.chains import build_rag_chain
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

st.set_page_config(page_title="Tire Industry Strategy RAG", layout="wide")
st.title("Tire Industry Competitor Analysis")

# --- UI Sidebar ---
st.sidebar.header("Analysis Mode")
mode = st.sidebar.radio(
    "Choose your data source:",
    ["Financial Extraction (RAG)", "Live Web Sentiment (Scraper)"]
)
st.sidebar.markdown("---")
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.rerun()


# Initialize pipelines
@st.cache_resource
def load_rag_pipeline():
    return build_rag_chain()

@st.cache_resource
def load_sentiment_pipeline():
    # A dedicated LLM just for analyzing the scraped web text
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    prompt = PromptTemplate.from_template("""
    You are an expert financial sentiment analyst. 
    Review the following recent web search results regarding a tire company.
    
    1. Determine if the overall public sentiment is POSITIVE, NEGATIVE, or NEUTRAL.
    2. Provide a brief summary of the main news driving this sentiment.
    
    Web Search Results:
    {web_context}
    """)
    return prompt | llm

rag_chain = load_rag_pipeline()
sentiment_chain = load_sentiment_pipeline()
web_search_tool = DuckDuckGoSearchResults()

# Chat interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Dynamic input prompt based on mode
placeholder_text = "Ask about financial performance..." if mode == "Financial Extraction (RAG)" else "Enter a company name (e.g., Michelin) to scrape live sentiment..."

if prompt := st.chat_input(placeholder_text):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if mode == "Financial Extraction (RAG)":
            with st.spinner("Scanning 2025 Annual Reports..."):
                try:
                    chat_history = []
                    for m in st.session_state.messages[:-1]:
                        role = "human" if m["role"] == "user" else "assistant"
                        chat_history.append((role, m["content"]))
                    
                    response = rag_chain.invoke({"input": prompt, "chat_history": chat_history})
                    answer = response["answer"]
                    st.markdown(answer)
                    
                except Exception as e:
                    answer = f"An error occurred. Details: {e}"
                    st.error(answer)
                    
        elif mode == "Live Web Sentiment (Scraper)":
            with st.spinner(f"Scraping the web for live news about {prompt}..."):
                try:
                    # 1. Scrape the live internet
                    search_query = f"recent news {prompt} tire company financial performance"
                    raw_search_results = web_search_tool.run(search_query)
                    
                    # 2. Pass the scraped data to the LLM for analysis
                    response = sentiment_chain.invoke({"web_context": raw_search_results})
                    answer = response.content
                    
                    st.markdown("### Live Sentiment Analysis")
                    st.markdown(answer)
                    with st.expander("View Raw Scraped Web Data"):
                        st.write(raw_search_results)
                        
                except Exception as e:
                    answer = f"An error occurred while scraping. Details: {e}"
                    st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})