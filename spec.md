# Spec

## Intent
Implements `intent/classifier.md`.

## Components

### classifier
- **What it does:** takes one support message, sends it to a model with instructions to answer in JSON, reads the reply, and prints one JSON object with `category`, `urgency` and `reason`. `eval.py` runs it on the five cases in `cases.json` and prints PASS or FAIL for each.
- **Language:** Python 3.9 or later, standard library only. **Why:** the `json` module is built in and last week's `chat.py` already makes the same HTTP call. Java was the alternative. It has no JSON parser in its standard library, so it needs either a library jar or a hand-written parser, and neither teaches anything this lab is about.
- **Model:** `minimax/minimax-m3` by default. **Why:** it is the class model and it answered correctly in Week 2 at about $0.0002 a question. The eval compares it against `xiaomi/mimo-v2.6-flash` on the same five cases. Both are cheap models. A frontier model is not compared this week because the lab names these two.
- **Interfaces:**
  - `python3 classify.py "<message>"` prints the JSON object on stdout and a usage line (model, tokens in, tokens out) on stderr.
  - `python3 eval.py` reads `cases.json`, prints one PASS or FAIL line per case, then a summary line with the pass count and total tokens.
  - Environment: `CHAT_BASE_URL`, `CHAT_MODEL`, and the key in `OPENROUTER_API_KEY` (or `CHAT_API_KEY` for a local model).
  - The request sets `max_tokens` to 500, because MiniMax M3 spends part of the budget on hidden reasoning.
- **Dependencies:** none beyond the Python standard library.

## Behavior
1. A clear billing message yields `category` `billing`.
2. A clear technical message yields `category` `technical`. When the customer cannot use the product, `urgency` is `high`.
3. A clear sales message yields `category` `sales`.
4. A message that fits two categories passes with either one.
5. A message that is not a support request yields `category` `unknown`.

In every case the output is one JSON object with exactly the three fields, `category` is one of `billing`, `technical`, `sales`, `unknown`, and `urgency` is one of `low`, `medium`, `high`.

## Failure handling
- **Reply is not JSON, or has text around it:** the program looks for the first `{` and the last `}` and parses what is between them. If that fails, it prints `{"category": "unknown", "urgency": "low", "reason": "model reply was not valid JSON"}`.
- **A field is missing or outside the allowed values:** same fallback, with the reason naming the bad field.
- **Empty reply:** same fallback, with the reason saying the reply was empty. This is the hidden-reasoning case from Week 2.
- **Fallbacks in the eval:** a fallback counts as FAIL, even on the `unknown` case, so a broken reply can never pass by accident.
- **Missing key or environment variable:** the program names the variable and exits without calling the model.
- **HTTP error or timeout (60 seconds):** the program prints the status and exits with a non-zero code. The eval records the case as FAIL and continues.

## Cost estimate
About 200 tokens in and up to 500 out per message. At MiniMax M3's Week 2 rate that is roughly $0.0003 to $0.0006 a message, so one eval run of five cases costs under half a cent per model. Fifty eval runs over the semester would cost about $0.15.

## Out of scope
From the intent: replying to the customer, routing, more than one message per run, languages other than English, retries, any web or graphical interface, training a model.

Ruled out by the design: the `response_format` parameter (not every model honors it, so the eval must not depend on it), and streaming.
