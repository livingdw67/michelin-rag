"""Input and output guardrails.

Input: reject empty or oversized questions and flag obvious prompt-injection attempts.
Output: every citation must point to a chunk that was actually retrieved, and its quote
must really appear in that chunk. Answers without a verified citation are withheld.
"""
import re
import unicodedata
from difflib import SequenceMatcher

from config.settings import settings

INJECTION_PATTERNS = [
    r"ignore (all |any |the )?(previous|prior|above) (instructions|rules)",
    r"disregard (the |your )?(system|previous) (prompt|instructions)",
    r"you are now",
    r"reveal (your|the) (system )?prompt",
    r"act as (?!an? (analyst|financial))",
]


NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


class GuardrailError(ValueError):
    """Raised when a question is rejected before reaching the model."""


def check_question(question):
    q = (question or "").strip()
    if not q:
        raise GuardrailError("Please enter a question.")
    if len(q) > settings.max_question_chars:
        raise GuardrailError(f"Questions are limited to {settings.max_question_chars} characters.")
    if any(re.search(p, q, re.IGNORECASE) for p in INJECTION_PATTERNS):
        raise GuardrailError("This assistant only answers questions about the tire company reports.")
    return q


def normalize(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[\s|*_]+", " ", text).strip()


def quote_in_text(quote, text, threshold=0.85):
    """True if the quote appears in the text, allowing for whitespace and minor formatting drift."""
    q, t = normalize(quote), normalize(text)
    if not q:
        return False
    if q in t:
        return True
    # Numbers must match exactly: a quote with a changed figure is a fabrication, not drift
    if any(num not in t for num in NUMBER.findall(q)):
        return False
    # Table quotes are often abbreviated ("Revenue … 4,430.1") or pair a value with its column header.
    # Accept them when every number matched exactly above and nearly all words appear in the chunk.
    words = [w for w in re.findall(r"[a-z]{3,}", q)]
    if NUMBER.search(q) and words and sum(w in t for w in words) / len(words) >= 0.8:
        return True
    # Fuzzy fallback: best-matching window of the same length
    matcher = SequenceMatcher(None, t, q, autojunk=False)
    match = matcher.find_longest_match(0, len(t), 0, len(q))
    start = max(0, match.a - match.b)
    window = t[start:start + len(q)]
    return SequenceMatcher(None, window, q, autojunk=False).ratio() >= threshold


def verify_citations(citations, retrieved):
    """Split citations into verified and rejected, checking ids and quotes against retrieved chunks."""
    by_id = {d.metadata["chunk_id"]: d for d in retrieved}
    verified, rejected = [], []
    for c in citations:
        doc = by_id.get(c.chunk_id)
        (verified if doc is not None and quote_in_text(c.quote, doc.page_content) else rejected).append(c)
    return verified, rejected
