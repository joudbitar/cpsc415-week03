# Intent: support message classifier

## Goal
A command-line program that takes one customer-support message, asks a language model to classify it, and prints one JSON object with three fields: `category`, `urgency`, and `reason`. A second program runs it on five known messages and prints PASS or FAIL for each.

## Who it is for
Me, learning how to get data out of a model and check it.

## Constraints
- Python 3.9 or later, standard library only.
- `category` is one of `billing`, `technical`, `sales`, `unknown`.
- `urgency` is one of `low`, `medium`, `high`.
- `high` means the customer cannot use the product, or money was taken wrongly.
- The eval checks `category` on all five messages. It checks `urgency` only where one answer is obvious.
- `reason` is one sentence.
- A message that is not a support request gets `unknown`.
- If the model's reply cannot be read as JSON, or a field has a value outside the lists above, the program still prints valid JSON: `category` is `unknown`, `urgency` is `low`, and `reason` says the reply could not be read. It does not crash.
- The base URL comes from `CHAT_BASE_URL`, the model from `CHAT_MODEL`, the key from `OPENROUTER_API_KEY`. No key in the code or the repository.
- Two models are compared on the same five messages: `minimax/minimax-m3` and `xiaomi/mimo-v2.6-flash`.
- Each classification costs well under 1 cent.
- Due Monday, October 5, 2026, 1:30 PM.

## Not in scope
- Replying to the customer or routing the message anywhere.
- More than one message per run.
- Languages other than English.
- Retrying after a bad reply.
- A web page or graphical interface.
- Training or fine-tuning a model.

## Success looks like
- `python3 classify.py "I was charged twice this month"` prints JSON with `category` set to `billing`.
- `python3 classify.py "What's a good pizza place near campus?"` prints JSON with `category` set to `unknown`.
- `python3 eval.py` prints five PASS or FAIL lines and a summary with the pass count and the tokens used.
- Changing only `CHAT_MODEL` reruns the same five messages on the other model.

## Open questions
None left.

**Approved by:** <your name>, <date>
