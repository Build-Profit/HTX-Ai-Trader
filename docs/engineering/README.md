# Engineering Docs

Owner: Engineering Lead

This folder is for collaboration rules, local setup, review expectations, and release hygiene.

## Working Rules

- Keep `main` runnable.
- Commit small, reviewable changes.
- Do not commit API keys, tokens, wallet keys, `.env` files, or local cache files.
- Prefer deterministic tests for strategy and backtest behavior.
- Any displayed metric must trace back to data and code.

## Suggested Git Flow

For fast hackathon work:

```bash
git checkout -b feature/<short-name>
git add .
git commit -m "Add <feature>"
git push origin feature/<short-name>
```

Then open a pull request into `main`.

If time is tight, direct push to `main` is acceptable only when:

- The change is small.
- The app still runs.
- The change does not overwrite another member's work.

## Review Checklist

- Does it match the PRD loop?
- Does it avoid guaranteed-return wording?
- Are metrics reproducible?
- Does it degrade cleanly when HTX API is unavailable?
- Is sensitive configuration excluded from Git?
