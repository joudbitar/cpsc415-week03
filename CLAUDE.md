# Project conventions

<!-- The agent reads this at the start of every session. Keep it short and current.
     Graded: does it reflect how the team actually works? -->

## What this repository is
A classifier for customer-support messages that prints JSON, with a five-case eval run on more than one model. The design is in [`spec.md`](spec.md).

## Commands
```
# run
python3 classify.py "<message>"
# eval
python3 eval.py
```

## Conventions
- Language: Python 3.9 or later, standard library only.
- Default model: `minimax/minimax-m3`. The eval also runs on `xiaomi/mimo-v2.6-flash`.
- File names are lowercase with underscores. Programs sit at the repository root.
- No tests are required this week. `eval.py` is the check.
- No branches or pull requests this week. Commit to `main`.

## Working rules

For an introductory lab, follow its explicitly assigned stages; the full chain below applies to major projects. Week 1 uses its own minimal repository.

- Write or update `intent/` and `spec.md` before code. Get `plan.md` approved before implementing.
- One feature per branch and pull request. Never push to `main` directly.
- Never commit `.env` or `.claude/settings.local.json`.
- This is the Week 3 introductory lab. Stages assigned: intent and spec.
  No plan.md, no branches or pull requests. Commit to main.
- Standard library only, except that Java may add one JSON library jar.

## Common mistakes
Things the agent got wrong before and must not repeat. Add to this list as they happen.
