"""Development / held-out split of the 400 questions, frozen before any tuning of the local system.

Round 1 (2026-10-22) put the local model through the full 400. Fixing it means looking at its failures,
and fixes tuned on the questions that score them would overstate the gain. So a quarter of every design cell
(company x type, each company pair, out of scope, injection) is set aside for development, with the cell's
wordings rotated so each gets its share; the other three quarters are held out. Tuning looks only at
development answers (and the golden set); the held-out questions are scored once, at the end of a round.

    python -m eval.factorial.split       # writes split.json and prints its balance
"""
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

from eval.factorial.design import SEED, WORDINGS, cell

HERE = Path(__file__).resolve().parent
SPLIT = HERE / "split.json"


def make_split(items):
    by_cell = defaultdict(list)
    for item in items:
        by_cell[cell(item)].append(item)
    dev = []
    for name, group in sorted(by_cell.items()):
        rng = random.Random(f"{SEED}:split:{name}")
        by_wording = {w: sorted((i for i in group if i["wording"] == w), key=lambda i: i["id"]) for w in WORDINGS}
        for w in WORDINGS:
            rng.shuffle(by_wording[w])
        order = list(WORDINGS)
        rng.shuffle(order)
        # Deal round-robin across wordings so the first picks cover different wordings
        dealt = [by_wording[w][k] for k in range(max(map(len, by_wording.values())))
                 for w in order if k < len(by_wording[w])]
        dev += [i["id"] for i in dealt[:max(1, round(len(group) / 4))]]
    dev = set(dev)
    return sorted(dev), sorted(i["id"] for i in items if i["id"] not in dev)


def load_split():
    return json.loads(SPLIT.read_text(encoding="utf-8"))


def main():
    items = [json.loads(line) for line in open(HERE / "questions.jsonl", encoding="utf-8") if line.strip()]
    dev, heldout = make_split(items)
    SPLIT.write_text(json.dumps({"frozen": "2026-10-22", "seed": SEED, "dev": dev, "heldout": heldout}, indent=1),
                     encoding="utf-8")
    meta = {i["id"]: i for i in items}
    print(f"dev {len(dev)}, held out {len(heldout)}")
    for name, ids in (("dev", dev), ("held out", heldout)):
        print(f"  {name:<9} type {dict(Counter(meta[i]['type'] for i in ids))}")
        print(f"  {'':<9} wording {dict(Counter(meta[i]['wording'] for i in ids))}")


if __name__ == "__main__":
    main()
