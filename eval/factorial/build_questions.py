"""Build eval/factorial/questions.jsonl and check it against the reports.

Checks (the build fails on any of them):
  1. every figure in values.py has its evidence string on its page
  2. every text, comparison, false-premise and injection item has each evidence string on one of its pages
  3. every not_found item's regexes match nothing in that company's report
  4. no question repeats one in eval/golden_set.jsonl
  5. rewrites.py covers exactly the items dealt the casual and terse wordings
  6. typo questions differ from the formal wording but keep every capitalized word and figure
  7. the wording design is balanced within every cell

Page text is read the way the index reads it: PyMuPDF text per page, plus the cached vision
transcription in data/ocr/ for image-only pages. Matching ignores whitespace and normalizes
ligatures and dashes, since PDF extraction varies in both.

Usage:
    python -m eval.factorial.build_questions
"""
import json
import re
import sys
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path

from config.settings import COMPANIES, settings
from eval.factorial.design import WORDINGS, add_typos, assign_wordings, balance_table
from eval.factorial.questions import ITEMS
from eval.factorial.rewrites import CASUAL, TERSE
from eval.factorial.values import V

HERE = Path(__file__).resolve().parent
OUT = HERE / "questions.jsonl"
GOLDEN = HERE.parent / "golden_set.jsonl"


def _norm(text):
    text = unicodedata.normalize("NFKC", text)
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("−", "-")):
        text = text.replace(a, b)
    return re.sub(r"\s+", "", text).lower()


def _flat(text):
    return " ".join(unicodedata.normalize("NFKC", text).split())


def _pdf_pages(path):
    try:
        import pymupdf
        with pymupdf.open(path) as pdf:
            return [page.get_text() for page in pdf]
    except ImportError:  # same text layer, different extractor; only used where PyMuPDF is unavailable
        from pypdf import PdfReader
        return [page.extract_text() or "" for page in PdfReader(str(path)).pages]


@lru_cache(maxsize=None)
def pages(company):
    """{page number: text}, with OCR transcriptions added for image-only pages."""
    texts = _pdf_pages(settings.data_dir / COMPANIES[company]["file"])
    out = {i + 1: t for i, t in enumerate(texts)}
    ocr_dir = settings.ocr_dir / company.lower()
    if ocr_dir.exists():
        for f in ocr_dir.glob("p*.md"):
            n = int(f.stem[1:])
            out[n] = out.get(n, "") + "\n" + f.read_text(encoding="utf-8")
    return out


@lru_cache(maxsize=None)
def _norm_page(company, page):
    return _norm(pages(company).get(page, ""))


LOOSE_MATCHES = []  # (company, page, evidence) that matched only through the token fallback


def on_page(company, page, evidence):
    """Exact (whitespace-insensitive) match, or, since extractors order table cells and columns
    differently, every token of the evidence appearing in order within 400 characters."""
    text = _norm_page(company, page)
    if _norm(evidence) in text:
        return True
    tokens = [_norm(t) for t in re.findall(r"[^\s|]+", evidence)]
    pos = start = text.find(tokens[0]) if tokens else -1
    while start != -1:
        pos, ok = start, True
        for t in tokens[1:]:
            pos = text.find(t, pos + 1)
            if pos == -1 or pos - start > 400:
                ok = False
                break
        if ok:
            LOOSE_MATCHES.append((company, page, evidence))
            return True
        start = text.find(tokens[0], start + 1)
    return False


def check_values():
    return [f"{k}: '{x.evidence}' not on {x.company} p{x.page}" for k, x in V.items() if not on_page(x.company, x.page, x.evidence)]


def check_item_evidence(item):
    if item["type"] in ("number", "calc", "not_found", "out_of_scope"):
        return []  # figures are checked in check_values; the others have no evidence
    companies = [c for c in item["company"].split(",") if c]
    problems = []
    for e in item.get("evidence", []):
        if not any(on_page(c, p, e) for c in companies for p in item["pages"]):
            problems.append(f"{item['id']}: '{e}' not on pages {item['pages']} of {companies}")
    return problems


def check_absent(item):
    flat = " ".join(_flat(t) for t in pages(item["company"]).values())
    problems = []
    for pattern in item["absent"]:
        m = re.search(pattern, flat, re.IGNORECASE)
        if m:
            problems.append(f"{item['id']}: /{pattern}/ matched '{flat[max(0, m.start() - 60):m.end() + 60]}'")
    return problems


def wording_text(item, wording):
    if wording == "formal":
        return item["question"]
    if wording == "casual":
        return CASUAL[item["id"]]
    if wording == "terse":
        return TERSE[item["id"]]
    return add_typos(item["question"], item["id"])


def _protected(text):
    return sorted(re.findall(r"\b[A-Z][\w'’.-]*|\d[\d,.]*", text))


def build():
    problems = check_values()
    wordings = assign_wordings(ITEMS)

    golden = {_norm(json.loads(line)["question"]) for line in open(GOLDEN, encoding="utf-8") if line.strip()}
    for want, table in (("casual", CASUAL), ("terse", TERSE)):
        assigned = {i for i, w in wordings.items() if w == want}
        problems += [f"{i}: assigned {want} but has no rewrite" for i in sorted(assigned - set(table))]
        problems += [f"{i}: has a {want} rewrite but is assigned {wordings.get(i)}" for i in sorted(set(table) - assigned)]

    rows = []
    for item in ITEMS:
        problems += check_item_evidence(item)
        if item["type"] == "not_found":
            problems += check_absent(item)
        wording = wordings[item["id"]]
        try:
            text = wording_text(item, wording)
        except KeyError:  # missing rewrite, already reported above
            text = item["question"]
        if _norm(item["question"]) in golden or _norm(text) in golden:
            problems.append(f"{item['id']}: repeats a golden-set question")
        if wording == "typo":
            if text == item["question"]:
                problems.append(f"{item['id']}: typo wording made no change")
            if _protected(text) != _protected(item["question"]):
                problems.append(f"{item['id']}: typo changed a name or figure")
        rows.append({**item, "canonical": item["question"], "question": text, "wording": wording})

    table = balance_table(ITEMS, wordings)
    problems += [f"cell {k} unbalanced: {v}" for k, v in table.items() if len(set(v.values())) > 1]
    if len({r["id"] for r in rows}) != len(rows):
        problems.append("duplicate ids")
    return rows, table, problems


def main():
    rows, table, problems = build()
    if problems:
        print(f"{len(problems)} problem(s):")
        print("\n".join(f"  {p}" for p in problems))
        sys.exit(1)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} questions to {OUT.relative_to(HERE.parent.parent)}")
    if LOOSE_MATCHES:
        print(f"{len(LOOSE_MATCHES)} evidence string(s) matched by in-order tokens rather than verbatim (layout differences):")
        for company, page, evidence in sorted(set(LOOSE_MATCHES)):
            print(f"  {company} p{page}: {evidence}")
    print("by type:", dict(Counter(r["type"] for r in rows)))
    print("by wording:", dict(Counter(r["wording"] for r in rows)))
    print(f"{'cell':34} " + " ".join(f"{w:>7}" for w in WORDINGS))
    for k, v in table.items():
        print(f"{k:34} " + " ".join(f"{v[w]:>7}" for w in WORDINGS))


if __name__ == "__main__":
    main()
