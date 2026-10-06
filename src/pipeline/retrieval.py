"""Hybrid retrieval: BM25 keyword search + vector search, merged with reciprocal rank fusion.

Keyword search catches exact terms and figures ("adjusted EBIT", "2025"); vector search
catches paraphrases. Company filtering is deterministic (name matching), so a question
about Goodyear can never be answered from Michelin's report.
"""
import json
import re
import threading

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from rank_bm25 import BM25Okapi

from config.settings import COMPANIES, settings
from src.pipeline.index import CHUNKS_FILE, COLLECTION, embeddings

TOKEN = re.compile(r"[a-z0-9]+(?:[.,][0-9]+)*")
PARENT_COMPANY = re.compile(r"parent[- ]company|statutory|compagnie g[ée]n[ée]rale|cgem", re.IGNORECASE)

EXPANSION_PROMPT = """Write 2 short search queries that would find the answer to this question in a company's \
annual report. Use the terminology annual reports use (for example: employees -> "global workforce", "headcount", "associates"; \
revenue -> "consolidated sales", "net sales"; profit -> "net income attributable to shareholders"). \
Keep every company name and year from the question.

Question: {question}"""


class SearchQueries(BaseModel):
    queries: list[str]


def tokenize(text):
    return TOKEN.findall(text.lower())


def detect_companies(question):
    """Companies named in the question; all companies if none are named."""
    q = question.lower()
    found = [name for name, meta in COMPANIES.items() if any(a in q for a in meta["aliases"])]
    return found or list(COMPANIES)


def reciprocal_rank_fusion(rankings, k):
    """Merge ranked lists of ids. Items ranked high in either list rise to the top."""
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)


class HybridRetriever:
    def __init__(self):
        with open(settings.index_dir / CHUNKS_FILE, encoding="utf-8") as f:
            self.chunks = [json.loads(line) for line in f]
        self.by_id = {c["chunk_id"]: c for c in self.chunks}
        self.bm25 = BM25Okapi([tokenize(c["text"]) for c in self.chunks])
        self.store = Chroma(collection_name=COLLECTION, embedding_function=embeddings(),
                            persist_directory=str(settings.index_dir))

    def _keyword(self, question, companies, scopes):
        scores = self.bm25.get_scores(tokenize(question))
        ranked = sorted(range(len(self.chunks)), key=lambda i: scores[i], reverse=True)
        hits = [self.chunks[i]["chunk_id"] for i in ranked
                if scores[i] > 0 and self.chunks[i]["company"] in companies and self.chunks[i]["scope"] in scopes]
        return hits[:settings.candidate_k]

    def _vector(self, question, companies, scopes):
        where = {"$and": [{"company": {"$in": companies}}, {"scope": {"$in": scopes}}]}
        docs = self.store.similarity_search(question, k=settings.candidate_k, filter=where)
        return [d.metadata["chunk_id"] for d in docs]

    def expand(self, question):
        """Extra search queries phrased the way annual reports word things. Falls back to none on error."""
        if not settings.query_expansion:
            return []
        try:
            llm = ChatOpenAI(model=settings.rewrite_model, api_key=settings.openai_api_key)
            return llm.with_structured_output(SearchQueries).invoke(EXPANSION_PROMPT.format(question=question)).queries[:2]
        except Exception:
            return []

    def _search(self, queries, companies, k, scopes):
        rankings = []
        for query in queries:
            rankings += [self._keyword(query, companies, scopes), self._vector(query, companies, scopes)]
        return reciprocal_rank_fusion(rankings, settings.rrf_k)[:k]

    def retrieve(self, question, k=None):
        k = k or settings.retriever_k
        companies = detect_companies(question)
        # Parent-company statutory accounts are searched only when the question asks for them
        scopes = ["group", "parent_company"] if PARENT_COMPANY.search(question) else ["group"]
        queries = [question] + self.expand(question)
        named = companies if 1 < len(companies) < len(COMPANIES) else []
        if named:
            # Comparisons: search each named company separately, with the other names removed so they
            # don't skew keyword matching, and give each company its own share of the context
            per = max(4, k // len(named) + 2)
            ids = []
            for company in named:
                stripped = []
                for query in queries:
                    for other in named:
                        if other != company:
                            for alias in COMPANIES[other]["aliases"]:
                                query = re.sub(alias, "", query, flags=re.IGNORECASE)
                    stripped.append(query)
                ids += self._search(stripped, [company], per, scopes)
        else:
            ids = self._search(queries, companies, k, scopes)
        return [self._to_document(cid) for cid in ids]

    def _to_document(self, chunk_id):
        c = self.by_id[chunk_id]
        return Document(page_content=c["text"], metadata={key: v for key, v in c.items() if key != "text"})


_retriever = None
_retriever_lock = threading.Lock()


def get_retriever():
    """Shared retriever. Created once under a lock: concurrent first calls would race to open Chroma."""
    global _retriever
    with _retriever_lock:
        if _retriever is None:
            _retriever = HybridRetriever()
    return _retriever
