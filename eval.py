"""Run the classifier on the cases in cases.json and print PASS or FAIL for each.

    python3 eval.py
"""

import json
import pathlib
import urllib.error

import classify


def judge(case, result, ok):
    """Returns '' on a pass, or the reason for the failure."""
    if not ok:
        # A replaced reply never passes, even when the case expects unknown.
        return f"fallback: {result['reason']}"
    if result["category"] not in case["category"]:
        return f"category {result['category']}, expected {' or '.join(case['category'])}"
    if "urgency" in case and result["urgency"] != case["urgency"]:
        return f"urgency {result['urgency']}, expected {case['urgency']}"
    return ""


def main():
    base_url, model, key = classify.settings()
    cases = json.loads(pathlib.Path(__file__).with_name("cases.json").read_text())
    passed = tokens_in = tokens_out = 0
    cost = 0.0
    for number, case in enumerate(cases, 1):
        try:
            result, ok, reply = classify.classify(case["message"], base_url, model, key)
        except urllib.error.HTTPError as error:
            print(f"FAIL {number}. {case['name']}: HTTP {error.code}")
            continue
        except (urllib.error.URLError, TimeoutError) as error:
            print(f"FAIL {number}. {case['name']}: no reply ({error})")
            continue
        usage = reply.get("usage") or {}
        tokens_in += usage.get("prompt_tokens") or 0
        tokens_out += usage.get("completion_tokens") or 0
        cost += usage.get("cost") or 0
        problem = judge(case, result, ok)
        passed += not problem
        got = f"{result['category']}/{result['urgency']}"
        print(f"{'FAIL' if problem else 'PASS'} {number}. {case['name']}: {got}"
              + (f" ({problem})" if problem else ""))
    print(f"{model}: {passed}/{len(cases)} passed · {tokens_in} in / {tokens_out} out · ${cost:.6f}")


if __name__ == "__main__":
    main()
