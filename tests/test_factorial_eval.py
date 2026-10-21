"""Tests for the 400-question factorial eval (eval/factorial). No API key needed."""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from eval.factorial import build_questions
from eval.factorial.design import WORDINGS, add_typos, assign_wordings, balance_table
from eval.factorial.grading import auto_check, number_matches, passes_by_status
from eval.factorial.questions import ITEMS
from eval.factorial.stats import (chi2_sf, firth_logit, fleiss_kappa, item_rates, logistic_model, wilson,
                                  wording_permutation)

BY_ID = {i["id"]: i for i in ITEMS}
COMMITTED = Path(build_questions.OUT)


# --- the question bank --------------------------------------------------------------------------

def test_bank_verifies_against_reports_and_matches_committed_file():
    """Every figure is on its page, every not-found answer is absent, and questions.jsonl is current."""
    rows, _, problems = build_questions.build()
    assert problems == []
    committed = [json.loads(line) for line in open(COMMITTED, encoding="utf-8")]
    assert committed == json.loads(json.dumps(rows, ensure_ascii=False))


def test_bank_size_and_ids():
    assert len(ITEMS) == 400
    assert len(BY_ID) == 400


def test_no_golden_set_question_is_repeated():
    golden = {json.loads(line)["question"].lower() for line in open("eval/golden_set.jsonl", encoding="utf-8") if line.strip()}
    assert not [i["id"] for i in ITEMS if i["question"].lower() in golden]


def test_calc_truths_are_computed_from_page_figures():
    assert BY_ID["GY-C05"]["truth"] == -30  # $796M operating cash flow - $826M capex
    assert BY_ID["MI-C16"]["truth"] == 1642  # €974M dividends + €668M buybacks
    assert BY_ID["MI-C09"]["truth"] == -767  # net debt €3,112M -> €2,345M, as the URD states
    assert round(BY_ID["CO-C06"]["truth"], 1) == 60.4  # free cash flow €603M -> €967M


# --- design -------------------------------------------------------------------------------------

def test_wording_is_balanced_in_every_cell_and_reproducible():
    w = assign_wordings(ITEMS)
    assert w == assign_wordings(ITEMS)
    for cell, counts in balance_table(ITEMS, w).items():
        assert len(set(counts.values())) == 1, cell
    assert set(w.values()) == set(WORDINGS)


def test_typos_change_text_but_not_names_or_figures():
    q = "What was Michelin's free cash flow before M&A in 2025?"
    t = add_typos(q, "TEST")
    assert t != q and t == add_typos(q, "TEST")
    for keep in ("Michelin's", "M&A", "2025"):
        assert keep in t


# --- grading ------------------------------------------------------------------------------------

@pytest.mark.parametrize("target,text,expected", [
    (18280, "net sales were $18,280 million", True),
    (18280, "about $18.3 billion", True),
    (18280, "about $19.3 billion", False),
    (2366, "€2.4 billion", True),
    (4430.1, "4.43 trillion yen", True),
    (-9.414661, "a net loss of about 9.4% of sales", True),
    (10.6, "10.9%", False),
    (3.03, "3%", True),
    (2.9, "3.0%", False),
    (1.064288, "a current ratio of 1.06", True),
])
def test_number_matching_is_rounding_and_scale_aware(target, text, expected):
    assert number_matches(target, text) is expected


def test_auto_check_by_type():
    assert auto_check(BY_ID["GY-N01"], "answered", "Net sales were $18,878 million in 2024.")
    assert not auto_check(BY_ID["GY-N01"], "answered", "Net sales were $18,280 million.")
    assert not auto_check(BY_ID["GY-N01"], "not_found", "$18,878 million")
    assert auto_check(BY_ID["GY-T01"], "answered", "The CFO is Christina Zamarro.")
    assert auto_check(BY_ID["X-MC5"], "answered", "Continental: €5,154 million vs Michelin €2,345 million.")
    assert not auto_check(BY_ID["X-MC5"], "answered", "Continental: €5,154 million.")
    assert auto_check(BY_ID["GY-U01"], "not_found", "") is None


def test_status_rules():
    assert passes_by_status(BY_ID["OS-01"], "out_of_scope") is True
    assert passes_by_status(BY_ID["OS-01"], "answered") is False
    assert passes_by_status(BY_ID["GY-U01"], "not_found") is True
    assert passes_by_status(BY_ID["GY-U01"], "answered") is None  # the judge decides
    assert passes_by_status(BY_ID["IJ-03"], "blocked") is True
    assert passes_by_status(BY_ID["IJ-03"], "answered") is False
    assert passes_by_status(BY_ID["IJ-07"], "answered") is None  # carries a real question
    assert passes_by_status(BY_ID["GY-N01"], "answered") is None


# --- statistics ---------------------------------------------------------------------------------

def test_chi2_tail_matches_reference_values():
    for x, df, p in [(3.84, 1, 0.050044), (7.8, 3, 0.050331), (12.3, 4, 0.015254), (1.0, 3, 0.801252)]:
        assert chi2_sf(x, df) == pytest.approx(p, abs=1e-6)


def test_wilson_interval():
    lo, hi = wilson(95, 100)
    assert lo == pytest.approx(0.8882, abs=1e-4) and hi == pytest.approx(0.9785, abs=1e-4)


def test_firth_stays_finite_under_complete_separation():
    X = np.column_stack([np.ones(20), np.r_[np.zeros(10), np.ones(10)]])
    y = np.r_[np.zeros(10), np.ones(10)]
    beta, _, _ = firth_logit(X, y)
    assert np.all(np.isfinite(beta))


def _synthetic(effect):
    """Single-company questions only, 3 runs; typos fail with probability `effect`."""
    rng = np.random.default_rng(0)
    w = assign_wordings(ITEMS)
    rows = []
    for item in ITEMS:
        if item["type"] not in ("number", "text", "calc", "false_premise", "not_found"):
            continue
        p = 0.95 - (effect if w[item["id"]] == "typo" else 0)
        for run in (1, 2, 3):
            rows.append({"id": item["id"], "run": run, "type": item["type"], "company": item["company"],
                         "wording": w[item["id"]], "correct": bool(rng.random() < p), "single": True,
                         "cell": f"{item['company']}|{item['type']}"})
    return pd.DataFrame(rows)


def test_model_and_permutation_test_find_a_planted_wording_effect():
    df = _synthetic(effect=0.4)
    items = item_rates(df)
    model = logistic_model(df)
    assert model["factor_tests"]["wording"]["p"] < 0.001
    typo = next(c for c in model["coefficients"] if c["term"] == "wording=typo")
    assert typo["odds_ratio"] < 0.3
    perm = wording_permutation(items, 500, np.random.default_rng(1))
    assert perm["p"] < 0.01


def test_permutation_test_is_quiet_without_an_effect():
    df = _synthetic(effect=0.0)
    perm = wording_permutation(item_rates(df), 500, np.random.default_rng(1))
    assert perm["p"] > 0.01


def test_run_stability_summary():
    df = _synthetic(effect=0.0)
    s = fleiss_kappa(item_rates(df))
    assert s["runs"] == 3 and s["always_right"] + s["always_wrong"] + s["flaky"] == s["questions"]
    assert -1 <= s["kappa"] <= 1 and not math.isnan(s["icc"])
