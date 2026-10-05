# Checks

Run on 2026-10-05 around 13:17 EDT. The coding agent ran the commands at my request. The key came from the macOS Keychain for each command and was never printed or saved.

Each run is `python3 eval.py` on the same five cases in `cases.json`, with only `CHAT_MODEL` changed.

| Model | Cases passed | Failed cases | Tokens in / out | Cost reported by OpenRouter |
|---|---|---|---|---|
| `minimax/minimax-m3` | 5 of 5 | none | 1321 / 511 | $0.000996 |
| `xiaomi/mimo-v2.6-flash` | 5 of 5 | none | 578 / 350 | $0.000169 |
| `typesafe/jev-router` | 5 of 5 | none | 570 / 243 | $0.000179 |

## Per-case answers

All three models gave the same category and urgency on every case.

| Case | Expected | All three models answered |
|---|---|---|
| 1. clear billing | billing, high | billing / high |
| 2. clear technical | technical, high | technical / high |
| 3. clear sales | sales (urgency not checked) | sales / low |
| 4. ambiguous: upgrade button broken | sales or technical | technical / medium |
| 5. not a support request | unknown | unknown / low |

## Failures

None on these runs, so there is nothing to sort into judgment calls and real failures. No reply needed the fallback: every reply parsed as JSON with allowed values.

That is one run per model. Five cases that every model passes do not separate the models, so the set is too easy to rank them. The only differences I can record are in the usage numbers.

## What differed

MiniMax M3 counted 1321 input tokens for the same five prompts that MiMo counted as 578 and the router as 570, more than double. It also cost about six times as much as MiMo for the same five answers ($0.000996 against $0.000169). I did not look up why the input counts differ.

On the ambiguous case all three chose technical over sales. None chose unknown.

## Parser check without a model

I fed `parse_reply` eight hand-written replies. JSON inside a code fence and JSON with prose around it were both read correctly. Plain prose, an empty reply, a JSON array, a category of `refund`, an urgency of `urgent`, and a missing reason each produced the `unknown` fallback with `ok` set to false, which the eval counts as FAIL.

## Not run

No local model: there is no Ollama or LM Studio on this laptop. The `response_format` extra was not tried.
