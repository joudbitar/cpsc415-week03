"""Run the classifier on a set of cases and print PASS or FAIL for each.

    python3 eval.py                                   # five cases, CHAT_MODEL
    python3 eval.py --cases cases_hard.json --runs 3  # harder set, three tries each
    python3 eval.py --models a/x,b/y                  # same cases, one column per model
"""

import argparse
import json
import pathlib
import urllib.error
from concurrent.futures import ThreadPoolExecutor

import classify


def judge(case, result, ok):
    """Returns '' on a pass, or the reason for the failure."""
    if not ok:
        # A replaced reply never passes, even when the case expects unknown.
        return f"fallback: {result['reason']}"
    if result["category"] not in case["category"]:
        return f"category {result['category']}, expected {' or '.join(case['category'])}"
    if "urgency" in case and result["urgency"] not in case["urgency"]:
        return f"urgency {result['urgency']}, expected {' or '.join(case['urgency'])}"
    return ""


def run_case(case, base_url, model, key):
    """One call. Returns {'answer', 'problem', 'usage'}; never raises on a failed call."""
    try:
        result, ok, reply = classify.classify(case["message"], base_url, model, key)
    except urllib.error.HTTPError as error:
        return {"answer": "no reply", "problem": f"HTTP {error.code}", "usage": {}}
    except (urllib.error.URLError, TimeoutError, ValueError) as error:
        return {"answer": "no reply", "problem": f"no reply ({error})", "usage": {}}
    return {"answer": f"{result['category']}/{result['urgency']}",
            "problem": judge(case, result, ok), "usage": reply.get("usage") or {}}


def run_model(cases, runs, base_url, model, key):
    """Returns one list of `runs` outcomes per case, in case order."""
    jobs = [(case, base_url, model, key) for case in cases for _ in range(runs)]
    with ThreadPoolExecutor(max_workers=6) as pool:
        outcomes = list(pool.map(lambda job: run_case(*job), jobs))
    return [outcomes[i * runs:(i + 1) * runs] for i in range(len(cases))]


def totals(per_case):
    outcomes = [o for case in per_case for o in case]
    return (sum(not o["problem"] for o in outcomes), len(outcomes),
            sum(o["usage"].get("prompt_tokens") or 0 for o in outcomes),
            sum(o["usage"].get("completion_tokens") or 0 for o in outcomes),
            sum(o["usage"].get("cost") or 0 for o in outcomes))


def summary(model, per_case):
    passed, total, tokens_in, tokens_out, cost = totals(per_case)
    return f"{model}: {passed}/{total} passed · {tokens_in} in / {tokens_out} out · ${cost:.6f}"


def print_one_model(cases, per_case, model, runs):
    for number, (case, outcomes) in enumerate(zip(cases, per_case), 1):
        passes = sum(not o["problem"] for o in outcomes)
        verdict = "PASS" if passes == runs else "FAIL"
        score = f" [{passes}/{runs}]" if runs > 1 else ""
        failures = sorted({f"{o['answer']} ({o['problem']})" for o in outcomes if o["problem"]})
        detail = "; ".join(failures) if failures else outcomes[0]["answer"]
        print(f"{verdict} {number}. {case['name']}{score}: {detail}")
    print(summary(model, per_case))


def print_matrix(cases, results, runs):
    """One row per case, one column per model, each cell the passes out of `runs`."""
    models = list(results)
    width = max(len(case["name"]) for case in cases) + 4
    print(" " * width + "  ".join(f"{m.split('/')[-1][:16]:>16}" for m in models))
    for i, case in enumerate(cases):
        cells = []
        for model in models:
            passes = sum(not o["problem"] for o in results[model][i])
            cells.append(f"{passes}/{runs}" + (" " if passes == runs else "*"))
        print(f"{i + 1:>2}. {case['name']:<{width - 4}}" + "  ".join(f"{c:>16}" for c in cells))
    print()
    for model in models:
        print(summary(model, results[model]))
    print("\n* failures:")
    for model in models:
        for i, case in enumerate(cases):
            for text in sorted({f"{o['answer']} ({o['problem']})"
                                for o in results[model][i] if o["problem"]}):
                print(f"  {model} · {i + 1}. {case['name']}: {text}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the classifier eval.")
    parser.add_argument("--cases", default="cases.json", help="case file (default cases.json)")
    parser.add_argument("--runs", type=int, default=1, help="tries per case (default 1)")
    parser.add_argument("--models", help="comma-separated models; default is CHAT_MODEL")
    args = parser.parse_args(argv)

    base_url, model, key = classify.settings()
    path = pathlib.Path(args.cases)
    if not path.is_absolute() and not path.exists():
        path = pathlib.Path(__file__).with_name(args.cases)
    cases = json.loads(path.read_text())

    if not args.models:
        print_one_model(cases, run_model(cases, args.runs, base_url, model, key), model, args.runs)
        return
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    results = {m: run_model(cases, args.runs, base_url, m, key) for m in models}
    print_matrix(cases, results, args.runs)


if __name__ == "__main__":
    main()
