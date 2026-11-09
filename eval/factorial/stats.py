"""Analyse the factorial eval: accuracy by factor, a logistic model, and checks on the grading.

Reads results/attempts_<system>.jsonl (one row per question x run) and writes, for that system:
  results/results_<system>.md     the report
  results/summary_<system>.json   every number in the report
  results/per_item_<system>.csv   one row per question: wording, runs passed, last judge note

Statistical choices
  * Unit of analysis. Runs of the same question are not independent, so intervals and tests treat
    the question as the unit: a cluster bootstrap over questions for accuracy intervals, cluster-robust
    (by question) standard errors in the model, and question-level pass rates in the permutation test.
    Attempt-level Wilson intervals are shown too, for comparison with the golden-set report.
  * Model. Firth-penalized logistic regression of attempt correctness on company, type and wording
    (main effects) for the 260 single-company questions. Firth's penalty keeps estimates finite when a
    cell is at or near 100%, which is the expected regime here. Joint Wald tests per factor use the
    cluster-robust covariance.
  * Wording is the only randomized factor (balanced within each cell, fixed seed). Its p-value comes
    from a stratified permutation test that re-deals wording labels within each design cell, exactly as
    the design did, so it needs no distributional assumption. Company and type effects are
    observational contrasts between fixed sets of questions.
  * Grading reliability. The LLM judge is compared with the model-free first pass (Cohen's kappa), and
    every disagreement is listed for a human read.

Usage:
    python -m eval.factorial.stats [--attempts attempts_openai.jsonl] [--perms 10000] [--boot 2000]
"""
import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from eval.factorial.design import SINGLE_COMPANY_TYPES, WORDINGS, cell
from eval.factorial.split import load_split

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
SEED = 20261021
COMPANIES = ["Michelin", "Goodyear", "Continental", "Bridgestone"]
TYPES = ["number", "text", "calc", "comparison", "false_premise", "not_found", "out_of_scope", "injection"]
ANSWERABLE = ["number", "text", "calc", "comparison", "false_premise"]


# --- distributions (scipy-free, so the eval adds no dependency) ---------------------------------

def norm_cdf(x):
    return 0.5 * math.erfc(-x / math.sqrt(2))


def norm_ppf(p):
    lo, hi = -10.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if norm_cdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


def chi2_sf(x, df):
    """Upper tail of the chi-square distribution: regularized upper incomplete gamma Q(df/2, x/2)."""
    if x <= 0:
        return 1.0
    a, z = df / 2.0, x / 2.0
    if z < a + 1:  # series for the lower gamma
        term = total = 1.0 / a
        n = a
        for _ in range(500):
            n += 1
            term *= z / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1.0 - total * math.exp(-z + a * math.log(z) - math.lgamma(a)))
    b, c, d = z + 1 - a, 1e300, 1 / (z + 1 - a)  # continued fraction for the upper gamma
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-15:
            break
    return math.exp(-z + a * math.log(z) - math.lgamma(a)) * h


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


# --- data ---------------------------------------------------------------------------------------

def load(attempts_name):
    questions = {q["id"]: q for q in map(json.loads, open(HERE / "questions.jsonl", encoding="utf-8"))}
    rows = [json.loads(line) for line in open(RESULTS / attempts_name, encoding="utf-8") if line.strip()]
    errors = [r for r in rows if r.get("status") == "error"]
    rows = [r for r in rows if r.get("status") != "error"]
    # keep the last attempt per (id, run) in case a run was repeated
    latest = {(r["id"], r["run"]): r for r in rows}
    df = pd.DataFrame(latest.values())
    df["correct"] = df["correct"].astype(bool)
    df["cell"] = df["id"].map(lambda i: cell(questions[i]))
    df["single"] = df["type"].isin(SINGLE_COMPANY_TYPES)
    return df, questions, errors


def item_rates(df):
    g = df.groupby("id")
    return pd.DataFrame({"rate": g["correct"].mean(), "runs": g["correct"].size(), "passed": g["correct"].sum(),
                         "type": g["type"].first(), "company": g["company"].first(), "wording": g["wording"].first(),
                         "cell": g["cell"].first()})


def cluster_boot_ci(rates, boot, rng):
    """95% interval for the mean question-level pass rate, resampling questions."""
    r = rates.to_numpy()
    if len(r) < 2:
        return (float("nan"), float("nan"))
    means = r[rng.integers(0, len(r), size=(boot, len(r)))].mean(axis=1)
    return (float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975)))


def accuracy_table(df, items, by, levels, boot, rng):
    out = []
    for level in levels:
        a = df[df[by] == level]
        i = items[items[by] == level]
        if a.empty:
            continue
        k, n = int(a["correct"].sum()), len(a)
        out.append({by: level, "questions": len(i), "attempts": n, "correct": k, "accuracy": k / n,
                    "wilson_95": wilson(k, n), "question_mean": float(i["rate"].mean()),
                    "cluster_boot_95": cluster_boot_ci(i["rate"], boot, rng)})
    return out


# --- Firth logistic regression with cluster-robust covariance ------------------------------------

def design_matrix(df, factors):
    cols, names = [np.ones(len(df))], ["(intercept)"]
    spans = {}
    for factor, levels in factors.items():
        start = len(names)
        for level in levels[1:]:  # treatment coding against the first level
            cols.append((df[factor] == level).to_numpy(float))
            names.append(f"{factor}={level}")
        spans[factor] = list(range(start, len(names)))
    return np.column_stack(cols), names, spans


def firth_logit(X, y, iters=100, tol=1e-8):
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ beta))
        w = p * (1 - p)
        info = X.T @ (X * w[:, None])
        info_inv = np.linalg.pinv(info)
        xw = X * np.sqrt(w)[:, None]
        h = np.einsum("ij,jk,ik->i", xw, info_inv, xw)  # leverages
        step = info_inv @ (X.T @ (y - p + h * (0.5 - p)))
        beta += step
        if np.max(np.abs(step)) < tol:
            break
    p = 1 / (1 + np.exp(-X @ beta))
    return beta, p, np.linalg.pinv(X.T @ (X * (p * (1 - p))[:, None]))


def cluster_cov(X, y, p, bread, clusters):
    scores = X * (y - p)[:, None]
    meat = np.zeros((X.shape[1], X.shape[1]))
    groups = pd.Series(range(len(clusters))).groupby(np.asarray(clusters)).indices
    for idx in groups.values():
        s = scores[idx].sum(axis=0)
        meat += np.outer(s, s)
    g = len(groups)
    return bread @ meat @ bread * g / max(1, g - 1)


def logistic_model(df):
    sub = df[df["single"]].copy()
    present = lambda col, levels: [l for l in levels if (sub[col] == l).any()]
    factors = {"company": present("company", COMPANIES), "type": present("type", list(SINGLE_COMPANY_TYPES)),
               "wording": present("wording", list(WORDINGS))}
    factors = {k: v for k, v in factors.items() if len(v) > 1}
    if sub.empty or not factors:
        return None
    X, names, spans = design_matrix(sub, factors)
    y = sub["correct"].to_numpy(float)
    beta, p, bread = firth_logit(X, y)
    cov = cluster_cov(X, y, p, bread, sub["id"].to_numpy())
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    coefs = []
    for j, name in enumerate(names):
        if j == 0:
            continue
        z = beta[j] / se[j] if se[j] > 0 else float("nan")
        coefs.append({"term": name, "odds_ratio": float(np.exp(beta[j])),
                      "ci_95": (float(np.exp(beta[j] - 1.96 * se[j])), float(np.exp(beta[j] + 1.96 * se[j]))),
                      "p": 2 * (1 - norm_cdf(abs(z))) if not math.isnan(z) else float("nan")})
    tests = {}
    for factor, idx in spans.items():
        b, v = beta[idx], cov[np.ix_(idx, idx)]
        stat = float(b @ np.linalg.pinv(v) @ b)
        tests[factor] = {"wald_chi2": stat, "df": len(idx), "p": chi2_sf(stat, len(idx)),
                         "reference": factors[factor][0]}
    return {"n_attempts": len(sub), "n_questions": int(sub["id"].nunique()), "coefficients": coefs, "factor_tests": tests}


# --- wording permutation test -------------------------------------------------------------------

def between_ss(rates, labels):
    grand = rates.mean()
    return sum(len(rates[labels == w]) * (rates[labels == w].mean() - grand) ** 2 for w in np.unique(labels))


def wording_permutation(items, perms, rng, subset=None):
    it = items if subset is None else items[items["type"].isin(subset)]
    if it.empty or it["wording"].nunique() < 2:
        return None
    rates, labels, cells = it["rate"].to_numpy(), it["wording"].to_numpy(), it["cell"].to_numpy()
    observed = between_ss(rates, labels)
    strata = [np.where(cells == c)[0] for c in np.unique(cells)]
    hits = 0
    shuffled = labels.copy()
    for _ in range(perms):
        for idx in strata:
            shuffled[idx] = rng.permutation(labels[idx])
        hits += between_ss(rates, shuffled) >= observed - 1e-12
    means = {w: float(rates[labels == w].mean()) for w in WORDINGS if (labels == w).any()}
    return {"questions": len(it), "between_wording_ss": float(observed), "p": (hits + 1) / (perms + 1),
            "permutations": perms, "question_mean_by_wording": means}


# --- grading and stability checks ---------------------------------------------------------------

def cohen_kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return float("nan")
    po = np.mean(a == b)
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def fleiss_kappa(items):
    full = items[items["runs"] == items["runs"].max()]
    n = int(full["runs"].max()) if not full.empty else 0
    if n < 2:
        return None
    k = full["passed"].to_numpy(float)
    p_i = (k * (k - 1) + (n - k) * (n - k - 1)) / (n * (n - 1))
    p1 = k.sum() / (len(k) * n)
    pe = p1 ** 2 + (1 - p1) ** 2
    kappa = float((p_i.mean() - pe) / (1 - pe)) if pe < 1 else float("nan")
    # one-way ANOVA intraclass correlation of attempts within a question, and what it means for precision
    q = len(k)
    msb = n * ((k / n - p1) ** 2).sum() / (q - 1) if q > 1 else float("nan")
    msw = (k * (1 - k / n)).sum() / (q * (n - 1))
    icc = float((msb - msw) / (msb + (n - 1) * msw)) if (msb + (n - 1) * msw) > 0 else float("nan")
    return {"runs": n, "questions": len(full), "kappa": kappa, "icc": icc,
            "effective_obs_per_question": float(n / (1 + (n - 1) * icc)) if not math.isnan(icc) else float("nan"),
            "always_right": int((k == n).sum()), "always_wrong": int((k == 0).sum()),
            "flaky": int(((k > 0) & (k < n)).sum())}


def judge_agreement(df):
    a = df[df["auto_correct"].notna() & df["type"].isin(ANSWERABLE)]
    if a.empty:
        return None
    judge, auto = a["correct"].astype(bool), a["auto_correct"].astype(bool)
    disagree = a[judge != auto]
    return {"attempts": len(a), "agreement": float((judge == auto).mean()), "kappa": cohen_kappa(judge, auto),
            "judge_yes_auto_no": int((judge & ~auto).sum()), "judge_no_auto_yes": int((~judge & auto).sum()),
            "disagreements": disagree[["id", "run", "correct", "auto_correct", "answer", "judge_reason"]]
            .fillna("").to_dict("records")}


def retrieval_split(df):
    a = df[df["type"].isin(ANSWERABLE) & df["retrieval_hit"].notna()] if "retrieval_hit" in df else pd.DataFrame()
    if a.empty:
        return None
    hit = a["retrieval_hit"].astype(bool)
    return {"attempts": len(a), "retrieval_hit_rate": float(hit.mean()),
            "accuracy_when_retrieved": float(a[hit]["correct"].mean()) if hit.any() else float("nan"),
            "accuracy_when_missed": float(a[~hit]["correct"].mean()) if (~hit).any() else float("nan"),
            "misses": int((~hit).sum()), "wrong_despite_retrieval": int((hit & ~a["correct"]).sum())}


# --- precision and power ------------------------------------------------------------------------

def mde(n1, n2, p0, alpha=0.05, power=0.80):
    """Smallest drop from p0 that a two-sided two-proportion z-test detects with the given power,
    treating each question as one observation (conservative: runs add little independent information)."""
    za, zb = norm_ppf(1 - alpha / 2), norm_ppf(power)
    for d in np.arange(0.005, p0, 0.0025):
        p1 = p0 - d
        pbar = (n1 * p0 + n2 * p1) / (n1 + n2)
        se0 = math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n2))
        se1 = math.sqrt(p0 * (1 - p0) / n1 + p1 * (1 - p1) / n2)
        if (d - za * se0) / se1 >= zb:
            return float(d)
    return float("nan")


def precision_table(items, p0):
    """Detectable effects for the group sizes this design actually has."""
    answerable = items[items["type"].isin(ANSWERABLE)]
    single = items[items["type"].isin(SINGLE_COMPANY_TYPES)]
    groups = [("wording level, all questions", len(items) // len(WORDINGS)),
              ("wording level, answerable questions", len(answerable) // len(WORDINGS)),
              ("company, single-company questions", len(single) // len(COMPANIES)),
              ("question type (number)", int((items["type"] == "number").sum())),
              ("question type (calc, text)", int((items["type"] == "calc").sum())),
              ("company x type cell (number)", int(((items["type"] == "number") & (items["company"] == "Michelin")).sum()))]
    return [{"comparison": label, "questions_per_group": n, "baseline": p0, "mde_80_power": mde(n, n, p0),
             "ci_half_width_at_baseline": 1.96 * math.sqrt(p0 * (1 - p0) / n)} for label, n in groups if n > 0]


def crosstab(items, rows, cols, row_levels, col_levels):
    """Question-mean accuracy for each row x column cell, with question counts."""
    out = {}
    for r in row_levels:
        out[r] = {}
        for c in col_levels:
            cell_items = items[(items[rows] == r) & (items[cols] == c)]
            out[r][c] = {"questions": len(cell_items), "question_mean": float(cell_items["rate"].mean()) if len(cell_items) else None}
    return out


def crosstab_md(tab, col_levels, label):
    lines = [f"| {label} | " + " | ".join(col_levels) + " |", "|---|" + "---:|" * len(col_levels)]
    for r, cells in tab.items():
        lines.append(f"| {r} | " + " | ".join(
            f"{pct(v['question_mean'])} ({v['questions']})" if v["questions"] else "–" for v in cells.values()) + " |")
    return lines


# --- report -------------------------------------------------------------------------------------

def pct(x):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}%"


def ci(t):
    return f"{pct(t[0])} – {pct(t[1])}"


def table_md(rows, key, label):
    lines = [f"| {label} | Questions | Attempts | Accuracy | Wilson 95% (attempts) | Question mean | Cluster bootstrap 95% |",
             "|---|---:|---:|---:|---|---:|---|"]
    for r in rows:
        lines.append(f"| {r[key]} | {r['questions']} | {r['attempts']} | {pct(r['accuracy'])} | {ci(r['wilson_95'])} | "
                     f"{pct(r['question_mean'])} | {ci(r['cluster_boot_95'])} |")
    return lines


def report(df, items, questions, errors, perms, boot):
    rng = np.random.default_rng(SEED)
    runs = int(df["run"].max())
    s = {"attempts": len(df), "questions": int(df["id"].nunique()), "runs": runs, "errors_excluded": len(errors)}
    groups = {"answerable": ANSWERABLE, "decline": ["not_found", "out_of_scope", "injection"], "all": TYPES}
    s["headline"] = {}
    for name, kinds in groups.items():
        a, i = df[df["type"].isin(kinds)], items[items["type"].isin(kinds)]
        k, n = int(a["correct"].sum()), len(a)
        s["headline"][name] = {"questions": len(i), "attempts": n, "accuracy": k / n if n else float("nan"),
                               "wilson_95": wilson(k, n), "question_mean": float(i["rate"].mean()),
                               "cluster_boot_95": cluster_boot_ci(i["rate"], boot, rng)}
    single, single_items = df[df["single"]], items[items["type"].isin(SINGLE_COMPANY_TYPES)]
    s["by_type"] = accuracy_table(df, items, "type", TYPES, boot, rng)
    s["by_company"] = accuracy_table(single, single_items, "company", COMPANIES, boot, rng)
    s["by_wording"] = accuracy_table(df, items, "wording", list(WORDINGS), boot, rng)
    s["by_wording_answerable"] = accuracy_table(df[df["type"].isin(ANSWERABLE)], items[items["type"].isin(ANSWERABLE)],
                                                "wording", list(WORDINGS), boot, rng)
    pairs = sorted(df.loc[df["type"] == "comparison", "company"].unique())
    s["by_pair"] = accuracy_table(df[df["type"] == "comparison"], items[items["type"] == "comparison"], "company", pairs, boot, rng)
    s["type_by_wording"] = crosstab(items, "type", "wording", TYPES, list(WORDINGS))
    s["company_by_type"] = crosstab(single_items, "company", "type", COMPANIES, list(SINGLE_COMPANY_TYPES))
    s["model"] = logistic_model(df)
    s["wording_permutation_all"] = wording_permutation(items, perms, rng)
    s["wording_permutation_answerable"] = wording_permutation(items, perms, rng, subset=ANSWERABLE)
    s["retrieval"] = retrieval_split(df)
    s["stability"] = fleiss_kappa(items)
    s["judge_vs_auto"] = judge_agreement(df)
    s["precision"] = precision_table(items, float(s["headline"]["answerable"]["question_mean"]))
    s["latency_median_s"] = float(df["seconds"].median())
    s["tokens_per_run"] = float(df["tokens"].sum() / runs) if "tokens" in df else float("nan")
    s["status_by_type"] = {t: dict(Counter(df.loc[df["type"] == t, "status"])) for t in TYPES if (df["type"] == t).any()}

    h = s["headline"]
    system = ""
    if "chat_model" in df and df["chat_model"].notna().any():
        system = f" · {df['system'].iloc[0]} system, answer model `{df['chat_model'].iloc[0]}`"
    md = [f"# Factorial Evaluation Results", "",
          f"{s['questions']} questions × {runs} run(s) = {s['attempts']} graded attempts{system}"
          + (f" ({len(errors)} errored attempts excluded; rerun to retry them)" if errors else "") + ".",
          "Design and method: [README](../README.md). Question-level intervals treat each question as the unit, "
          "since runs of the same question are not independent.", "",
          "## Headline", "",
          "| Block | Questions | Accuracy (attempts) | Wilson 95% | Question mean | Cluster bootstrap 95% |", "|---|---:|---:|---|---:|---|"]
    for name, label in [("answerable", "Answerable (number, text, calc, comparison, false premise)"),
                        ("decline", "Should decline or block (not found, out of scope, injection)"), ("all", "All")]:
        r = h[name]
        md.append(f"| {label} | {r['questions']} | {pct(r['accuracy'])} | {ci(r['wilson_95'])} | {pct(r['question_mean'])} | "
                  f"{ci(r['cluster_boot_95'])} |")
    md += ["", "## By question type", "", *table_md(s["by_type"], "type", "Type"),
           "", "## By company (single-company questions)", "", *table_md(s["by_company"], "company", "Company"),
           "", "## By wording", "", "All 400 questions:", "", *table_md(s["by_wording"], "wording", "Wording"),
           "", "Answerable questions only:", "", *table_md(s["by_wording_answerable"], "wording", "Wording")]
    for key, label in [("wording_permutation_all", "all questions"), ("wording_permutation_answerable", "answerable questions")]:
        w = s[key]
        if w:
            md += ["", f"Stratified permutation test of wording ({label}, {w['permutations']:,} re-deals within design cells): "
                       f"p = {w['p']:.3f}."]
    md += ["", "Question-mean accuracy by type and wording (questions per cell in brackets):", "",
           *crosstab_md(s["type_by_wording"], list(WORDINGS), "Type"),
           "", "## Company by type (single-company questions)", "",
           *crosstab_md(s["company_by_type"], list(SINGLE_COMPANY_TYPES), "Company"),
           "", "## Comparisons by company pair", "", *table_md(s["by_pair"], "company", "Pair")]

    m = s["model"]
    if m:
        md += ["", "## Logistic model (single-company questions)", "",
               f"Firth-penalized logistic regression, {m['n_attempts']} attempts on {m['n_questions']} questions, "
               "standard errors clustered by question. Odds ratios are against the reference level.", "",
               "| Factor | Reference | Wald χ² | df | p |", "|---|---|---:|---:|---:|"]
        for f, t in m["factor_tests"].items():
            md.append(f"| {f} | {t['reference']} | {t['wald_chi2']:.2f} | {t['df']} | {t['p']:.3f} |")
        md += ["", "| Term | Odds ratio | 95% CI | p |", "|---|---:|---|---:|"]
        for c in m["coefficients"]:
            md.append(f"| {c['term']} | {c['odds_ratio']:.2f} | {c['ci_95'][0]:.2f} – {c['ci_95'][1]:.2f} | {c['p']:.3f} |")

    r = s["retrieval"]
    if r:
        md += ["", "## Retrieval or generation?", "",
               f"Evidence was retrieved in {pct(r['retrieval_hit_rate'])} of answerable attempts. Accuracy was "
               f"{pct(r['accuracy_when_retrieved'])} when it was and {pct(r['accuracy_when_missed'])} when it wasn't; "
               f"{r['wrong_despite_retrieval']} wrong answers had the evidence in hand (a generation or reasoning failure) "
               f"and {r['misses']} attempts never retrieved it."]
    st = s["stability"]
    if st:
        md += ["", "## Run-to-run stability", "",
               f"Across {st['runs']} runs, {st['always_right']} questions were always right, {st['always_wrong']} always wrong "
               f"and {st['flaky']} varied. Fleiss' κ across runs = {st['kappa']:.2f}. The intraclass correlation of attempts "
               f"within a question is {st['icc']:.2f}, so {st['runs']} runs are worth about {st['effective_obs_per_question']:.1f} "
               "independent observations per question: extra runs mostly re-measure the same question, and more questions "
               "buy more precision than more runs."]
    j = s["judge_vs_auto"]
    if j:
        md += ["", "## Grading check: LLM judge vs. model-free first pass", "",
               f"{j['attempts']} answerable attempts: agreement {pct(j['agreement'])}, Cohen's κ = {j['kappa']:.2f}. "
               f"The judge passed {j['judge_yes_auto_no']} that the first pass didn't, and failed {j['judge_no_auto_yes']} "
               "that it passed. Each disagreement deserves a read; the first pass misses paraphrased names and unusual "
               "number formats, and the judge can be lenient on near-misses.", ""]
        if j["disagreements"]:
            md += ["| ID | Run | Judge | First pass | Judge's reason |", "|---|---:|---|---|---|"]
            for d in j["disagreements"][:40]:
                reason = " ".join(str(d["judge_reason"]).replace("|", "/").split())[:140]
                md.append(f"| {d['id']} | {d['run']} | {'pass' if d['correct'] else 'fail'} | "
                          f"{'pass' if d['auto_correct'] else 'fail'} | {reason} |")
    md += ["", "## Precision of this design", "",
           f"Smallest drop from the observed answerable accuracy ({pct(s['precision'][0]['baseline'])}) detectable with 80% power "
           "(two-sided α = 0.05, one observation per question):", "",
           "| Comparison | Questions per group | Detectable drop | 95% CI half-width |", "|---|---:|---:|---:|"]
    for p in s["precision"]:
        md.append(f"| {p['comparison']} | {p['questions_per_group']} | {pct(p['mde_80_power'])} | ±{pct(p['ci_half_width_at_baseline'])} |")

    fails = items[items["rate"] < 1].sort_values(["rate", "id"])
    md += ["", "## Questions that failed at least once", ""]
    if fails.empty:
        md.append("None.")
    else:
        md += ["| ID | Type | Wording | Passed | Question | Note (most recent failure) |", "|---|---|---|---:|---|---|"]
        for qid, row in fails.iterrows():
            last = df[(df["id"] == qid) & ~df["correct"]].sort_values("run").iloc[-1]
            note = last.get("judge_reason") if isinstance(last.get("judge_reason"), str) and last.get("judge_reason") else f"status: {last['status']}"
            note = " ".join(str(note).replace("|", "/").split())[:150]
            question = questions[qid]["question"].replace("|", "/")
            md.append(f"| {qid} | {row['type']} | {row['wording']} | {int(row['passed'])}/{int(row['runs'])} | {question} | {note} |")
    md += ["", f"Median latency {s['latency_median_s']:.1f} s · about {s['tokens_per_run']:,.0f} tokens per run (answers and grading).", ""]
    return s, "\n".join(md)


def suffix(attempts_name):
    """attempts_openai.jsonl -> "_openai"; anything else keeps its own stem."""
    stem = Path(attempts_name).stem
    return stem[len("attempts"):] if stem.startswith("attempts") else f"_{stem}"


def main(attempts_name, perms, boot, subset=None):
    df, questions, errors = load(attempts_name)
    tag = suffix(attempts_name)
    if subset:  # "dev" or "heldout" (eval/factorial/split.py)
        df = df[df["id"].isin(load_split()[subset])].reset_index(drop=True)
        tag += f"_{subset}"
    items = item_rates(df)
    summary, md = report(df, items, questions, errors, perms, boot)
    (RESULTS / f"results{tag}.md").write_text(md, encoding="utf-8")
    (RESULTS / f"summary{tag}.json").write_text(json.dumps(summary, indent=2, default=float), encoding="utf-8")
    last_reason = df.sort_values("run").groupby("id")["judge_reason"].last() if "judge_reason" in df else None
    out = items.join(last_reason) if last_reason is not None else items
    out.to_csv(RESULTS / f"per_item{tag}.csv")
    h = summary["headline"]
    print(f"answerable {pct(h['answerable']['accuracy'])}, decline {pct(h['decline']['accuracy'])}, "
          f"all {pct(h['all']['accuracy'])} over {summary['attempts']} attempts")
    print(f"wrote {RESULTS / f'results{tag}.md'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempts", default="attempts_openai.jsonl")
    parser.add_argument("--perms", type=int, default=10000)
    parser.add_argument("--boot", type=int, default=2000)
    parser.add_argument("--subset", choices=["dev", "heldout"], help="only the development or held-out questions")
    args = parser.parse_args()
    main(args.attempts, args.perms, args.boot, args.subset)
