"""Factorial design: which wording each item is asked in, and how typos are made.

Factors
  company   Goodyear, Michelin, Continental, Bridgestone (single-company items)
  type      number, text, calc, false_premise, not_found (single-company);
            comparison, out_of_scope, injection are their own blocks
  wording   formal, casual, terse, typo

Every item is asked once, in one wording. Within each cell (company x type for single-company
items; company pair for comparisons; the out-of-scope and injection blocks) the items are shuffled
with a fixed seed and dealt the four wordings in turn, so each wording gets the same number of items
per cell and the assignment is random with respect to item content. Wording is therefore a
between-item factor, crossed with company and type.

Typos are generated, not hand-written: two words of five or more letters (four, if a question has
too few) get one edit each
(transposition, deletion, doubling or a neighbouring key). Company names, people's names, figures and
other capitalized words are never altered, so a typo question still names its company correctly; the
deterministic company router is not what this factor tests.
"""
import random
import re
from collections import defaultdict

SEED = 20261021
WORDINGS = ("formal", "casual", "terse", "typo")
SINGLE_COMPANY_TYPES = ("number", "text", "calc", "false_premise", "not_found")

KEYBOARD_NEIGHBOURS = {
    "a": "sqwz", "b": "vngh", "c": "xvdf", "d": "sfer", "e": "wrds", "f": "dgrt", "g": "fhty", "h": "gjyu",
    "i": "uojk", "j": "hkui", "k": "jlio", "l": "kop", "m": "nj", "n": "bmhj", "o": "iplk", "p": "ol",
    "q": "wa", "r": "etdf", "s": "adwe", "t": "ryfg", "u": "yihj", "v": "cbfg", "w": "qeas", "x": "zcsd",
    "y": "tugh", "z": "xas",
}


def cell(item):
    if item["type"] in SINGLE_COMPANY_TYPES:
        return f"{item['company']}|{item['type']}"
    if item["type"] == "comparison":
        return f"pair:{item['company']}"
    return item["type"]


def assign_wordings(items, seed=SEED):
    """Return {item id: wording}, balanced within each cell."""
    by_cell = defaultdict(list)
    for item in items:
        by_cell[cell(item)].append(item["id"])
    rng = random.Random(seed)
    out = {}
    for key in sorted(by_cell):
        ids = sorted(by_cell[key])
        rng.shuffle(ids)
        offset = rng.randrange(len(WORDINGS))  # so leftover items in uneven cells don't always go to "formal"
        for i, item_id in enumerate(ids):
            out[item_id] = WORDINGS[(i + offset) % len(WORDINGS)]
    return out


def _edit(word, rng):
    i = rng.randrange(1, len(word) - 2)  # keep first and last letters, as most real typos do
    kind = rng.choice(("swap", "drop", "double", "neighbour"))
    if kind == "swap":
        return word[:i] + word[i + 1] + word[i] + word[i + 2:]
    if kind == "drop":
        return word[:i] + word[i + 1:]
    if kind == "double":
        return word[:i] + word[i] + word[i:]
    ch = word[i].lower()
    return word[:i] + rng.choice(KEYBOARD_NEIGHBOURS.get(ch, ch)) + word[i + 1:]


def add_typos(text, item_id, n=2):
    """Deterministically misspell `n` lowercase words of 5+ letters."""
    rng = random.Random(f"{SEED}:{item_id}")
    tokens = re.split(r"(\W+)", text)
    candidates = [i for i, t in enumerate(tokens) if re.fullmatch(r"[a-z]{5,}", t)]
    if len(candidates) < n:  # short questions: allow four-letter words too
        candidates = [i for i, t in enumerate(tokens) if re.fullmatch(r"[a-z]{4,}", t)]
    for i in sorted(rng.sample(candidates, min(n, len(candidates)))):
        tokens[i] = _edit(tokens[i], rng)
    return "".join(tokens)


def balance_table(items, wordings):
    """Counts per cell and wording, for the design report."""
    table = defaultdict(lambda: dict.fromkeys(WORDINGS, 0))
    for item in items:
        table[cell(item)][wordings[item["id"]]] += 1
    return dict(sorted(table.items()))
