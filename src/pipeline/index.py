"""Build the search indexes: a Chroma vector store plus a saved chunk list for BM25.

Usage:
    python -m src.pipeline.index
"""
import json
import shutil

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from config.settings import COMPANIES, settings
from src.pipeline.documents import chunk_documents, load_company

CHUNKS_FILE = "chunks.jsonl"
COLLECTION = "annual_reports"
PAGE_CACHE = settings.data_dir / "cache"


def load_company_cached(company):
    """Parsing ~1,250 pages for tables is slow, so parsed pages are cached until the PDF changes."""
    pdf = settings.data_dir / COMPANIES[company]["file"]
    cache = PAGE_CACHE / f"{company.lower()}.jsonl"
    if cache.exists() and cache.stat().st_mtime > pdf.stat().st_mtime:
        with open(cache, encoding="utf-8") as f:
            return [Document(page_content=r.pop("text"), metadata=r) for r in map(json.loads, f)]
    docs = load_company(company)
    PAGE_CACHE.mkdir(parents=True, exist_ok=True)
    with open(cache, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps({"text": d.page_content, **d.metadata}, ensure_ascii=False) + "\n")
    return docs


def embeddings():
    return OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)


def build_index():
    chunks = []
    for company in COMPANIES:
        docs = load_company_cached(company)
        company_chunks = chunk_documents(docs)
        kinds = {k: sum(c.metadata["kind"] == k for c in company_chunks) for k in ("text", "table", "ocr")}
        print(f"{company:<12} {len(company_chunks):>5} chunks  {kinds}")
        chunks.extend(company_chunks)

    if settings.index_dir.exists():
        shutil.rmtree(settings.index_dir)
    settings.index_dir.mkdir(parents=True)

    with open(settings.index_dir / CHUNKS_FILE, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps({"text": c.page_content, **c.metadata}, ensure_ascii=False) + "\n")

    store = Chroma(collection_name=COLLECTION, embedding_function=embeddings(),
                   persist_directory=str(settings.index_dir))
    batch = 500
    for start in range(0, len(chunks), batch):
        part = chunks[start:start + batch]
        store.add_documents(part, ids=[c.metadata["chunk_id"] for c in part])
    print(f"Indexed {len(chunks):,} chunks into {settings.index_dir}")


if __name__ == "__main__":
    build_index()
