"""Classify one customer-support message and print JSON.

    python3 classify.py "I was charged twice this month"

Needs CHAT_BASE_URL, CHAT_MODEL and a key in CHAT_API_KEY or OPENROUTER_API_KEY.
"""

import json
import os
import sys
import urllib.error
import urllib.request

MAX_TOKENS = 500
CATEGORIES = ("billing", "technical", "sales", "unknown")
URGENCIES = ("low", "medium", "high")

SYSTEM_PROMPT = (
    "You classify one customer-support message. Reply with one JSON object and "
    "nothing else, with exactly these fields:\n"
    '  "category": "billing", "technical", "sales" or "unknown"\n'
    '  "urgency": "low", "medium" or "high"\n'
    '  "reason": one sentence\n'
    "Use \"unknown\" when the message is not a support request. Urgency is "
    "\"high\" when the customer cannot use the product or money was taken wrongly."
)


def build_request(model, message):
    return {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        # OpenRouter adds the dollar cost to `usage`; other servers ignore this.
        "usage": {"include": True},
    }


def fallback(why):
    return {"category": "unknown", "urgency": "low", "reason": why}


def parse_reply(text):
    """Returns (result, ok). ok is False when the reply had to be replaced."""
    if not text or not text.strip():
        return fallback("model reply was empty"), False
    # Models often wrap the JSON in prose or a code fence, so take the outermost braces.
    start, end = text.find("{"), text.rfind("}")
    try:
        data = json.loads(text[start:end + 1])
    except ValueError:
        return fallback("model reply was not valid JSON"), False
    if not isinstance(data, dict):
        return fallback("model reply was not a JSON object"), False
    for field, allowed in (("category", CATEGORIES), ("urgency", URGENCIES)):
        if data.get(field) not in allowed:
            return fallback(f"model reply had a bad {field}: {data.get(field)!r}"), False
    reason = data.get("reason")
    if not isinstance(reason, str) or not reason.strip():
        return fallback("model reply had no reason"), False
    return {"category": data["category"], "urgency": data["urgency"], "reason": reason.strip()}, True


def settings(env=os.environ):
    base_url = env.get("CHAT_BASE_URL", "").rstrip("/")
    model = env.get("CHAT_MODEL")
    key = env.get("CHAT_API_KEY") or env.get("OPENROUTER_API_KEY")
    missing = [name for name, value in [("CHAT_BASE_URL", base_url), ("CHAT_MODEL", model),
                                        ("OPENROUTER_API_KEY", key)] if not value]
    if missing:
        sys.exit(f"missing environment variable: {', '.join(missing)}")
    return base_url, model, key


def classify(message, base_url, model, key):
    """Returns (result, ok, reply). Raises urllib.error.URLError on a failed call."""
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(build_request(model, message)).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        reply = json.load(response)
    choices = reply.get("choices") or [{}]
    text = (choices[0].get("message") or {}).get("content")
    result, ok = parse_reply(text)
    return result, ok, reply


def usage_line(reply):
    usage = reply.get("usage") or {}
    cost = usage.get("cost")
    cost = f"${cost:.6f}" if isinstance(cost, (int, float)) else "cost not reported"
    return (f"{reply.get('model', '?')} · {usage.get('prompt_tokens', '?')} in / "
            f"{usage.get('completion_tokens', '?')} out · {cost}")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.exit('usage: python3 classify.py "<message>"')
    base_url, model, key = settings()
    try:
        result, _, reply = classify(argv[0], base_url, model, key)
    except urllib.error.HTTPError as error:
        sys.exit(f"request failed: HTTP {error.code}: {error.read().decode()[:300]}")
    except urllib.error.URLError as error:
        sys.exit(f"could not reach {base_url}: {error.reason}")
    print(json.dumps(result, indent=2))
    print(usage_line(reply), file=sys.stderr)


if __name__ == "__main__":
    main()
