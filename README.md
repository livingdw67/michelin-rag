# Tire Industry Competitor Analysis: Dual-Engine RAG & Live Sentiment

## Project Overview
This application was built as a technical assessment to compare Michelin against major competitors (Goodyear, Continental, Bridgestone). Rather than relying on a single static data source, this application utilizes a dual-engine architecture:
1. **Financial Extraction (RAG):** A Local Vector Database querying 2025 Annual Reports for hard financial metrics and strategic direction.
2. **Live Web Sentiment (Scraper):** An autonomous web-scraping agent that searches the live internet to gauge current public perception and recent news headwinds.

## Technical Architecture
* **Orchestration:** LangChain (History-Aware Retrieval & Tool-calling Agents)
* **LLM:** OpenAI (`gpt-3.5-turbo` / `gpt-4o`)
* **Vector Database:** ChromaDB (Local, Persistent)
* **Web Scraping:** DuckDuckGo Search API
* **Frontend UI:** Streamlit
* **Deployment:** Fully containerized via Docker and Docker Compose

## Data Sources
* **Internal Data:** 2025 Annual/Strategic Reports (PDFs) from Michelin, Goodyear, Continental, and Bridgestone.
* **External Data:** Live, unstructured web search results via DuckDuckGo.

---

## Setup & Execution Instructions

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
* An OpenAI API Key.

### 1. Environment Setup
Clone the repository and navigate to the project directory:
```bash
git clone [https://github.com/Livingdw67/michelin-rag.git](https://github.com/Livingdw67/michelin-rag.git)
cd michelin-rag
