"""Turn annual report PDFs into page-aware chunks with citation metadata.

Each chunk records its company, source document, and page number so every answer
can cite exactly where a fact came from. Financial tables are kept intact as
Markdown, and image-only pages are transcribed once with a vision model and cached.
"""
import base64
from concurrent.futures import ThreadPoolExecutor

import pymupdf
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI

from config.settings import COMPANIES, settings

OCR_PROMPT = (
    "Transcribe all text on this annual report page exactly as written. "
    "Render tables as Markdown tables and keep every number, unit, and footnote marker. "
    "Do not summarize, translate, or add commentary. Output only the transcription."
)


def transcribe_page(client, png, out_path):
    """Transcribe an image-only page with the vision model, caching the result on disk."""
    if out_path.exists():
        return out_path.read_text(encoding="utf-8")
    response = client.chat.completions.create(
        model=settings.vision_model,
        messages=[{"role": "user", "content": [
            {"type": "text", "text": OCR_PROMPT},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(png).decode()}"}},
        ]}],
    )
    text = response.choices[0].message.content or ""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return text


def load_company(company, client=None):
    """Return one Document per page of text, plus one per extracted table."""
    meta = COMPANIES[company]
    pdf = pymupdf.open(settings.data_dir / meta["file"])
    docs, image_pages = [], []

    for index, page in enumerate(pdf):
        page_no = index + 1
        base = {"company": company, "doc": meta["doc"], "page": page_no}
        text = page.get_text()
        if len(text.strip()) < settings.min_page_chars and page.get_images():
            image_pages.append((page_no, page))
            continue
        docs.append(Document(page_content=text, metadata={**base, "kind": "text"}))
        for table in page.find_tables().tables:
            markdown = table.to_markdown()
            if markdown.count("|") > 8:  # skip layout boxes detected as one-cell "tables"
                docs.append(Document(page_content=markdown, metadata={**base, "kind": "table"}))

    if image_pages:
        client = client or OpenAI(api_key=settings.openai_api_key)
        out_dir = settings.ocr_dir / company.lower()
        # Render sequentially (PyMuPDF is not thread-safe); only the API calls run in parallel
        jobs = [(out_dir / f"p{no:03d}.md", None if (out_dir / f"p{no:03d}.md").exists()
                 else page.get_pixmap(dpi=130).tobytes("png")) for no, page in image_pages]
        with ThreadPoolExecutor(max_workers=6) as pool:
            texts = pool.map(lambda job: transcribe_page(client, job[1], job[0]), jobs)
            for (page_no, _), text in zip(image_pages, texts):
                docs.append(Document(page_content=text, metadata={
                    "company": company, "doc": meta["doc"], "page": page_no, "kind": "ocr"}))
    return docs


def chunk_documents(docs):
    """Split page text into overlapping chunks; keep tables whole unless very large."""
    splitter = RecursiveCharacterTextSplitter(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    table_splitter = RecursiveCharacterTextSplitter(chunk_size=6000, chunk_overlap=0, separators=["\n"])
    # Transcribed pages contain Markdown tables; split on paragraph breaks so a table's header stays with its rows
    ocr_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200, separators=["\n\n", "\n"])
    chunks = []
    for doc in docs:
        kind_splitter = {"table": table_splitter, "ocr": ocr_splitter}.get(doc.metadata["kind"], splitter)
        pieces = kind_splitter.split_documents([doc])
        for piece in pieces:
            if len(piece.page_content.strip()) < 40:
                continue
            m = piece.metadata
            piece.metadata["chunk_id"] = f"{m['company']}-p{m['page']}-{m['kind']}-{len(chunks)}"
            # Parent-company statutory accounts report different (smaller) figures than the consolidated group
            parent_ranges = COMPANIES[m["company"]].get("parent_company_pages", [])
            piece.metadata["scope"] = ("parent_company" if any(a <= m["page"] <= b for a, b in parent_ranges)
                                       else "group")
            # Contextual header: a chunk that never names its company (e.g. a bare table) still matches
            # searches for that company and document
            piece.page_content = f"[{m['doc']}, page {m['page']}]\n{piece.page_content}"
            chunks.append(piece)
    return chunks
