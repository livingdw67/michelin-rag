from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from config import settings
from config.prompts import RAG_PROMPT_TEMPLATE, CONTEXTUALIZE_Q_PROMPT

def build_rag_chain():
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory=settings.DB_DIR, 
        embedding_function=embeddings
    )
    
    llm = ChatOpenAI(model=settings.MODEL_NAME, temperature=settings.TEMPERATURE)
    
    # --- NEW: Define Metadata Schema for the AI ---
    metadata_field_info = [
        AttributeInfo(
            name="company",
            description="The name of the tire company. Valid options are: Michelin, Goodyear, Continental, Bridgestone",
            type="string",
        ),
    ]
    document_content_description = "Financial and strategic annual reports from tire manufacturers."
    
    # --- NEW: Create the Self-Querying Retriever ---
    # This acts as a brain BEFORE the search. It turns "What is Michelin's revenue?" 
    # into a hard filter: WHERE company = 'Michelin'
    base_retriever = SelfQueryRetriever.from_llm(
        llm,
        vectorstore,
        document_content_description,
        metadata_field_info,
        enable_limit=True,
        search_kwargs={"k": settings.RETRIEVER_K}
    )
    
    # Wrap it in the conversational memory we built earlier
    history_aware_retriever = create_history_aware_retriever(
        llm, base_retriever, CONTEXTUALIZE_Q_PROMPT
    )
    
    # Assemble the final pipeline
    question_answer_chain = create_stuff_documents_chain(llm, RAG_PROMPT_TEMPLATE)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    
    return rag_chain