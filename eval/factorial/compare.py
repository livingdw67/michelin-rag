"""Paired comparison of two systems on the same 400 questions (e.g. OpenAI vs. local Ollama models).

Both systems answer identical questions and are graded by the same OpenAI judge, so every question
gives a matched pair. Writes results/comparison.md and results/comparison.json.

  * Headline difference with a paired bootstrap interval over questions, and a sign-flip
    permutation test on per-question differences (each question's pass rate across its runs).
  * McNemar on the first run (exact and mid-p), with Newcombe's interval for a paired difference,
    for comparison with single-run evaluations.
  * The gap by question type, wording and company.
  * A Firth logistic model on both systems' attempts with system x wording and system x type
    interactions, clustered by question: does the smaller model fall further on typos, terse
    queries, or calculations?
  * The questions only one system gets right, with both answers, and how each system's answers end
    (answered, declined, blocked) by question type.

Usage:
    python -m eval.factorial.compare                                   # openai vs local
    python -m eval.factorial.compare --a attempts_openai.jsonl --b attempts_local.jsonl
"""
import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from eval.factorial.design import SINGLE_COMPANY_TYPES, WORDINGS
from eval.factorial.split import load_split
from eval.factorial.stats import (ANSWERABLE, COMPANIES, SEED, TYPES, chi2_sf, cluster_cov, firth_logit,
                                  norm_cdf, pct, wilson)

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"


def load(name):
    rows = [json.loads(line) for line in open(RESULTS / name, encoding="utf-8") if line.strip()]
    rows = [r for r in rows if r.get("status") != "error"]
    df = pd.DataFrame({(r["id"], r["run"]): r for r in rows}.values())
    df["correct"] = df["correct"].astype(bool)
    return df


def label(df, fallback):
    if "chat_model" in df and df["chat_model"].notna().any():
        return f"{df['system'].iloc[0]} ({df['chat_model'].iloc[0]})"
    return fallback


# --- paired tests -------------------------------------------------------------------------------

def mcnemar(b, c):
    """Exact two-sided McNemar p and mid-p for b and c discordant pairs."""
    n, k = b + c, min(b, c)
    if n == 0:
        return 1.0, 1.0
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    exact = min(1.0, 2 * tail)
    mid = min(1.0, 2 * (tail - 0.5 * math.comb(n, k) / 2 ** n))
    return exact, mid


def newcombe_paired(a, b, c, d, z=1.96):
    """Newcombe (1998) method 10: score interval for p1 - p2 from paired binary data.
    a = both right, b = first only, c = second only, d = neither."""
    n = a + b + c + d
    p1, p2 = (a + b) / n, (a + c) / n
    l1, u1 = wilson(a + b, n, z)
    l2, u2 = wilson(a + c, n, z)
    denom = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    phi = (a * d - b * c) / denom if denom > 0 else 0.0
    diff = p1 - p2
    lower = diff - math.sqrt(max(0.0, (p1 - l1) ** 2 - 2 * phi * (p1 - l1) * (u2 - p2) + (u2 - p2) ** 2))
    upper = diff + math.sqrt(max(0.0, (u1 - p1) ** 2 - 2 * phi * (u1 - p1) * (p2 - l2) + (p2 - l2) ** 2))
    return diff, (lower, upper)


def paired_diff(rates_a, rates_b, rng, boot=2000, perms=10000):
    """Mean per-question difference, paired bootstrap 95% CI, and sign-flip permutation p."""
    d = (rates_a - rates_b).to_numpy()
    n = len(d)
    if n == 0:
        return {"questions": 0}
    means = d[rng.integers(0, n, size=(boot, n))].mean(axis=1)
    observed = abs(d.mean())
    flips = rng.choice([-1.0, 1.0], size=(perms, n))
    p = (1 + int((np.abs((flips * d).mean(axis=1)) >= observed - 1e-12).sum())) / (perms + 1)
    return {"questions": n, "a": float(rates_a.mean()), "b": float(rates_b.mean()), "difference": float(d.mean()),
            "ci_95": (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))), "p": p}


# --- interaction model --------------------------------------------------------------------------

def interaction_model(stacked):
    """Firth logistic: correct ~ system + company + type + wording + system:wording + system:type,
    single-company questions, clustered by question (both systems' attempts share a cluster)."""
    sub = stacked[stacked["type"].isin(SINGLE_COMPANY_TYPES)].reset_index(drop=True)
    if sub.empty:
        return None
    is_b = (sub["sys"] == "b").to_numpy(float)
    cols, names = [np.ones(len(sub)), is_b], ["(intercept)", "system=b"]
    spans = {"system": [1]}
    levels = {"company": COMPANIES, "type": list(SINGLE_COMPANY_TYPES), "wording": list(WORDINGS)}
    for factor, lv in levels.items():
        lv = [l for l in lv if (sub[factor] == l).any()]
        start = len(names)
        for l in lv[1:]:
            cols.append((sub[factor] == l).to_numpy(float))
            names.append(f"{factor}={l}")
        spans[factor] = list(range(start, len(names)))
    for factor in ("wording", "type"):
        lv = [l for l in levels[factor] if (sub[factor] == l).any()]
        start = len(names)
        for l in lv[1:]:
            cols.append(is_b * (sub[factor] == l).to_numpy(float))
            names.append(f"system=b x {factor}={l}")
        spans[f"system x {factor}"] = list(range(start, len(names)))
    X = np.column_stack(cols)
    y = sub["correct"].to_numpy(float)
    beta, p, bread = firth_logit(X, y)
    cov = cluster_cov(X, y, p, bread, sub["id"].to_numpy())
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    tests = {}
    for name, idx in spans.items():
        if not idx:
            continue
        bvec, v = beta[idx], cov[np.ix_(idx, idx)]
        stat = float(bvec @ np.linalg.pinv(v) @ bvec)
        tests[name] = {"wald_chi2": stat, "df": len(idx), "p": chi2_sf(stat, len(idx))}
    terms = []
    for j, name in enumerate(names[1:], 1):
        z = beta[j] / se[j] if se[j] > 0 else float("nan")
        terms.append({"term": name, "odds_ratio": float(np.exp(beta[j])),
                      "ci_95": (float(np.exp(beta[j] - 1.96 * se[j])), float(np.exp(beta[j] + 1.96 * se[j]))),
                      "p": 2 * (1 - norm_cdf(abs(z))) if not math.isnan(z) else float("nan")})
    return {"attempts": len(sub), "questions": int(sub["id"].nunique()), "tests": tests, "terms": terms}


# --- report -------------------------------------------------------------------------------------

def compare(a, b, name_a, name_b, boot=2000, perms=10000):
    rng = np.random.default_rng(SEED)
    common = sorted(set(a["id"]) & set(b["id"]))
    a, b = a[a["id"].isin(common)], b[b["id"].isin(common)]
    meta = a.groupby("id")[["type", "company", "wording"]].first()
    ra, rb = a.groupby("id")["correct"].mean(), b.groupby("id")["correct"].mean()
    q = meta.join(ra.rename("a")).join(rb.rename("b"))

    out = {"a": name_a, "b": name_b, "questions": len(common),
           "runs": {"a": int(a["run"].max()), "b": int(b["run"].max())}}
    out["overall"] = paired_diff(q["a"], q["b"], rng, boot, perms)
    ans = q[q["type"].isin(ANSWERABLE)]
    out["answerable"] = paired_diff(ans["a"], ans["b"], rng, boot, perms)

    first = sorted(set(a["run"]) & set(b["run"]))[0]
    fa = a[a["run"] == first].set_index("id")["correct"]
    fb = b[b["run"] == first].set_index("id")["correct"]
    ids = fa.index.intersection(fb.index)
    fa, fb = fa[ids], fb[ids]
    cells = {"both": int((fa & fb).sum()), "a_only": int((fa & ~fb).sum()), "b_only": int((~fa & fb).sum()),
             "neither": int((~fa & ~fb).sum())}
    exact, mid = mcnemar(cells["a_only"], cells["b_only"])
    diff, ci = newcombe_paired(cells["both"], cells["a_only"], cells["b_only"], cells["neither"])
    out["mcnemar_first_run"] = {"run": int(first), **cells, "exact_p": exact, "mid_p": mid,
                                "difference": diff, "newcombe_95": ci}

    def by(factor, levels):
        return [{factor: l, **paired_diff(q.loc[q[factor] == l, "a"], q.loc[q[factor] == l, "b"], rng, boot, perms)}
                for l in levels if (q[factor] == l).any()]
    out["by_type"] = by("type", TYPES)
    out["by_wording"] = by("wording", list(WORDINGS))
    single = q[q["type"].isin(SINGLE_COMPANY_TYPES)]
    out["by_company"] = [{"company": c, **paired_diff(single.loc[single["company"] == c, "a"],
                                                       single.loc[single["company"] == c, "b"], rng, boot, perms)}
                         for c in COMPANIES if (single["company"] == c).any()]

    stacked = pd.concat([a.assign(sys="a"), b.assign(sys="b")], ignore_index=True)
    out["model"] = interaction_model(stacked)
    out["status"] = {s: {t: dict(df.loc[df["type"] == t, "status"].value_counts()) for t in TYPES if (df["type"] == t).any()}
                     for s, df in (("a", a), ("b", b))}
    out["latency_median_s"] = {"a": float(a["seconds"].median()), "b": float(b["seconds"].median())}

    last = lambda df: df.sort_values("run").groupby("id").last()
    la, lb = last(a), last(b)
    split = q[(q["a"] - q["b"]).abs() >= 0.5].copy()
    split["gap"] = split["a"] - split["b"]
    out["split_questions"] = [{"id": i, "type": r["type"], "wording": r["wording"], "a": float(r["a"]), "b": float(r["b"]),
                               "question": la.loc[i, "question"], "answer_a": str(la.loc[i].get("answer", "")),
                               "answer_b": str(lb.loc[i].get("answer", "")), "status_b": lb.loc[i, "status"]}
                              for i, r in split.sort_values(["gap", "type"], ascending=[False, True]).iterrows()]
    return out


def _pp(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:+.1f} pts"


def _row(label_, r):
    if not r.get("questions"):
        return f"| {label_} | 0 | | | | | |"
    return (f"| {label_} | {r['questions']} | {pct(r['a'])} | {pct(r['b'])} | {_pp(r['difference'])} | "
            f"{_pp(r['ci_95'][0])} to {_pp(r['ci_95'][1])} | {r['p']:.3f} |")


def markdown(c):
    head = ["| | Questions | A | B | A − B | Paired bootstrap 95% | Sign-flip p |", "|---|---:|---:|---:|---:|---|---:|"]
    md = ["# System Comparison", "",
          f"**A:** {c['a']} ({c['runs']['a']} run(s)) · **B:** {c['b']} ({c['runs']['b']} run(s)) · "
          f"{c['questions']} matched questions, both graded by the same OpenAI judge.", "",
          "Each question contributes its pass rate across runs; differences are paired by question.", "",
          "## Headline", "", *head, _row("All questions", c["overall"]), _row("Answerable", c["answerable"])]
    m = c["mcnemar_first_run"]
    md += ["", f"First run only (run {m['run']}): both right {m['both']}, A only {m['a_only']}, B only {m['b_only']}, "
               f"neither {m['neither']}. McNemar exact p = {m['exact_p']:.4f} (mid-p {m['mid_p']:.4f}); "
               f"A − B = {_pp(m['difference'])}, Newcombe 95% {_pp(m['newcombe_95'][0])} to {_pp(m['newcombe_95'][1])}."]
    for key, title, col in [("by_type", "By question type", "type"), ("by_wording", "By wording", "wording"),
                            ("by_company", "By company (single-company questions)", "company")]:
        md += ["", f"## {title}", "", *[h.replace("| |", f"| {col.capitalize()} |", 1) for h in head[:1]], head[1]]
        md += [_row(r[col], r) for r in c[key]]
    mod = c["model"]
    if mod:
        md += ["", "## Where does B lose ground?", "",
               f"Firth logistic regression on {mod['attempts']} attempts ({mod['questions']} single-company questions, both "
               "systems), errors clustered by question. The interaction tests ask whether B's gap changes with wording or "
               "question type.", "", "| Term set | Wald χ² | df | p |", "|---|---:|---:|---:|"]
        md += [f"| {k} | {t['wald_chi2']:.2f} | {t['df']} | {t['p']:.3f} |" for k, t in mod["tests"].items()]
        md += ["", "| Term | Odds ratio | 95% CI | p |", "|---|---:|---|---:|"]
        md += [f"| {t['term']} | {t['odds_ratio']:.2f} | {t['ci_95'][0]:.2f} – {t['ci_95'][1]:.2f} | {t['p']:.3f} |"
               for t in mod["terms"] if t["term"].startswith("system")]
    md += ["", "## How answers end", "", "| Type | A | B |", "|---|---|---|"]
    for t in TYPES:
        sa, sb = c["status"]["a"].get(t), c["status"]["b"].get(t)
        if sa or sb:
            fmt = lambda s: ", ".join(f"{k} {v}" for k, v in sorted((s or {}).items(), key=lambda kv: -kv[1]))
            md.append(f"| {t} | {fmt(sa)} | {fmt(sb)} |")
    md += ["", f"Median latency: A {c['latency_median_s']['a']:.1f} s, B {c['latency_median_s']['b']:.1f} s.",
           "", "## Questions the systems split on", "",
           "Pass rates differ by at least half (most recent answers shown).", ""]
    if not c["split_questions"]:
        md.append("None.")
    else:
        md += ["| ID | Type | Wording | A | B | Question | A's answer | B's answer |", "|---|---|---|---:|---:|---|---|---|"]
        clip = lambda s: " ".join(str(s).replace("|", "/").split())[:120]
        md += [f"| {r['id']} | {r['type']} | {r['wording']} | {pct(r['a'])} | {pct(r['b'])} | {clip(r['question'])} | "
               f"{clip(r['answer_a'])} | {clip(r['answer_b'])} |" for r in c["split_questions"]]
    return "\n".join(md) + "\n"


def main(file_a, file_b, boot, perms, subset=None):
    a, b = load(file_a), load(file_b)
    name = "comparison"
    if subset:  # "dev" or "heldout" (eval/factorial/split.py)
        ids = load_split()[subset]
        a, b, name = a[a["id"].isin(ids)], b[b["id"].isin(ids)], f"comparison_{subset}"
    c = compare(a, b, label(a, file_a), label(b, file_b), boot, perms)
    (RESULTS / f"{name}.json").write_text(json.dumps(c, indent=2, default=float), encoding="utf-8")
    (RESULTS / f"{name}.md").write_text(markdown(c), encoding="utf-8")
    o = c["overall"]
    print(f"{c['a']} {pct(o['a'])} vs {c['b']} {pct(o['b'])}: difference {_pp(o['difference'])} "
          f"(95% {_pp(o['ci_95'][0])} to {_pp(o['ci_95'][1])}), p = {o['p']:.3f}")
    print(f"wrote {RESULTS / f'{name}.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--a", default="attempts_openai.jsonl")
    parser.add_argument("--b", default="attempts_local.jsonl")
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--perms", type=int, default=10000)
    parser.add_argument("--subset", choices=["dev", "heldout"], help="only the development or held-out questions")
    args = parser.parse_args()
    main(args.a, args.b, args.boot, args.perms, args.subset)
