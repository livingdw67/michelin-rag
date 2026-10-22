"""Tests for the answer-now, grade-later runner (eval/factorial/deferred.py). No API key needed."""
import json

import pytest

from eval.factorial import deferred
from eval.run_eval import Grade


def test_pricing_counts_openai_models_and_ignores_local_ones():
    usage = {"gpt-5.4-mini-2026-03-17": {"input_tokens": 1_000_000, "output_tokens": 100_000},
             "gpt-5.4-nano-2026-03-17": {"input_tokens": 1_000_000, "output_tokens": 0},
             "qwen2.5-7b-16k": {"input_tokens": 9_999_999, "output_tokens": 9_999_999}}
    assert deferred.dollars(usage) == pytest.approx(0.75 + 0.45 + 0.20)


def test_a_partial_last_line_is_skipped(tmp_path):
    path = tmp_path / "pending.jsonl"
    path.write_text('{"id": "A", "run": 1}\n{"id": "B", "ru', encoding="utf-8")
    assert deferred.read_rows(path) == [{"id": "A", "run": 1}]


class FakeJudge:
    def __init__(self):
        self.calls = 0

    def invoke(self, prompt):
        self.calls += 1
        return Grade(correct=True, reason="matches")


def test_grading_rules(tmp_path, monkeypatch):
    base = {"run": 1, "system": "local", "company": "Goodyear", "wording": "formal", "question": "q"}
    rows = [
        {**base, "id": "N1", "type": "number", "status": "not_found", "judge_prompt": "p", "correct": None},
        {**base, "id": "N2", "type": "number", "status": "answered", "judge_prompt": "p", "correct": None},
        {**base, "id": "N3", "type": "number", "status": "error", "error": "LengthFinishReasonError: limit"},
        {**base, "id": "N4", "type": "number", "status": "error", "error": "APIConnectionError: down"},
        {**base, "id": "N5", "type": "number", "status": "error", "error": "LengthFinishReasonError: limit"},
        {**base, "id": "N5", "type": "number", "status": "answered", "judge_prompt": "p", "correct": None},
        {**base, "id": "O1", "type": "out_of_scope", "status": "out_of_scope", "correct": True},
    ]
    (tmp_path / "pending_local.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    judge = FakeJudge()
    monkeypatch.setattr(deferred.R, "RESULTS", tmp_path)
    monkeypatch.setattr(deferred.R, "judge", lambda: judge)

    deferred.grade("pending_local.jsonl", max_dollars=1.0)
    out = {r["id"]: r for r in map(json.loads, open(tmp_path / "attempts_local.jsonl", encoding="utf-8"))}

    assert out["N1"]["correct"] is False  # answerable but not answered: wrong, no judge call needed
    assert out["N2"]["correct"] is True and "judge_prompt" not in out["N2"]
    assert out["N3"]["status"] == "failed" and out["N3"]["correct"] is False  # ran past its output limit
    assert "N4" not in out  # an outage is retried, not scored
    assert out["N5"]["status"] == "failed"  # the first attempt counts; a retry doesn't get a second chance
    assert out["O1"]["correct"] is True
    assert judge.calls == 1

    deferred.grade("pending_local.jsonl", max_dollars=1.0)  # rerunning grades nothing twice
    assert judge.calls == 1
