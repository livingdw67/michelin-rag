import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import settings

def ingest_documents():
    data_dir = settings.DATA_DIR
    documents = []
    
    # 1. Load PDFs and Inject Metadata
    print("Scanning data directory for PDFs...")
    for file in os.listdir(data_dir):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_dir, file)
            company_name = file.split('_')[0].capitalize() # Extracts 'Michelin' from 'michelin_2025.pdf'
            
            print(f"Loading {company_name} report...")
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            
            # Stamp every page with the company name
            for doc in docs:
                doc.metadata['company'] = company_name
                
            documents.extend(docs)

    if not documents:
        print("No documents found. Please add PDFs.")
        return

    # 2. Split and Save
    print(f"Loaded {len(documents)} pages. Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Initializing embeddings and saving to ChromaDB at {settings.DB_DIR}...")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.DB_DIR
    )
    print(f"Success! Vector database saved.")

if __name__ == "__main__":
    ingest_documents()