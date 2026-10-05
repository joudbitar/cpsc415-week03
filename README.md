# Support message classifier

Takes one customer-support message and prints JSON with a category (`billing`, `technical`, `sales` or `unknown`), an urgency (`low`, `medium` or `high`) and a one-sentence reason. `eval.py` runs it on five known messages and prints PASS or FAIL for each.

Built for CPSC 415 Week 3 from [`intent/classifier.md`](intent/classifier.md) and [`spec.md`](spec.md).

## Run it

Python 3.9 or newer, standard library only.

```bash
export CHAT_BASE_URL=https://openrouter.ai/api/v1
export CHAT_MODEL=minimax/minimax-m3
export OPENROUTER_API_KEY=...   # never in a file in this repo
python3 classify.py "I was charged twice for my subscription this month."
python3 eval.py
```

```text
PASS 1. clear billing: billing/high
PASS 2. clear technical: technical/high
PASS 3. clear sales: sales/low
PASS 4. ambiguous: upgrade button broken: technical/medium
PASS 5. not a support request: unknown/low
minimax/minimax-m3: 5/5 passed · 1321 in / 511 out · $0.000996
```

To compare models, change only `CHAT_MODEL` and run `eval.py` again.

## The five cases

| Case | Message | Passes with | What it is there to catch |
|---|---|---|---|
| 1 | "I was charged twice for my subscription this month." | billing, urgency high | A model that misses the easy case, or does not treat a wrong charge as urgent |
| 2 | "The app crashes every time I log in, I can't use it at all." | technical, urgency high | Same for a blocked customer |
| 3 | "Do you offer a discount for student teams of 10?" | sales | A pre-purchase question. Urgency is a judgment call, so it is not checked |
| 4 | "I want to upgrade to Pro but the upgrade button gives an error." | sales or technical | A message that fits two categories. Catches a model that gives up and says unknown |
| 5 | "What's a good pizza place near campus?" | unknown | A model that forces every message into a real category |

## Results

| Model | Cases passed | Tokens in / out | Cost |
|---|---|---|---|
| `minimax/minimax-m3` | 5 of 5 | 1321 / 511 | $0.000996 |
| `xiaomi/mimo-v2.6-flash` | 5 of 5 | 578 / 350 | $0.000169 |
| `typesafe/jev-router` | 5 of 5 | 570 / 243 | $0.000179 |

All three gave the same answer on every case, including technical on the ambiguous one. MiniMax M3 counted more than twice the input tokens for the same prompts and cost about six times what MiMo did. One run each, so these are observations. Details are in [`CHECKS.md`](CHECKS.md).

Five passes out of five on every model also means my cases are too easy to tell the models apart.

## What I corrected

In the intent, I deleted a "support team that reads every message by hand" that the agent invented as the user. It is only me. I also defined `high` urgency (the customer is blocked, or money was taken wrongly) and limited the urgency check to cases where one answer is obvious.

In the spec, I added a third run on `typesafe/jev-router`. The draft compared only the two cheap class models, and I wanted to see whether a router that picks the model for each request did any better. On these five cases it did not.

I also had to settle one thing the draft raised. A broken reply prints `unknown`, and case 5 expects `unknown`, so a broken reply could pass by accident. I chose to count every fallback as FAIL.

## One line I can explain

```python
start, end = text.find("{"), text.rfind("}")
```

That is in `parse_reply` in `classify.py`. Models often wrap the JSON in a code fence or add a sentence before it. This line finds the first `{` and the last `}` in the reply, and the next line hands only that slice to `json.loads`. If the slice is not JSON, or a field has a value outside the allowed lists, the program prints the `unknown` fallback and marks the reply as not ok, which `eval.py` counts as FAIL.

## How it was built

Harness: Claude Code. Model: Claude Opus 5.5, on my Claude subscription. The agent drafted the intent and the spec, I chose between the options and approved each one, and the agent wrote `classify.py`, `eval.py` and the first draft of the cases, which I picked. The program's own calls go through my OpenRouter account.
