---
status: active
progress: All Unit 3 and Unit 4 README sections written; criteria 1–5 MET after the price fix
next_date:
updated: 2026-10-26
---

## Now
- README complete for Units 3 and 4. Final read-through before submission.

## Next
- Optional: swap the two empty criterion 5 queries, weight title/category matches in search (both listed under What's Still Broken).

## Decisions
- 2026-10-26: M5 fix: `create_fit_card` checks the caption for the exact price ("$24"); retries once, then appends "($24 on depop.)". Criterion 4 revision dropped; criterion stays as originally written. Before-run: criterion 4 MISSED 3/5 (two cards said "twenty-four bucks").
- 2026-10-26: Expanded `_STOPWORDS` in `tools.py` (grammar words, request filler like "looking"/"something", leftover price/size words like "under"/"size"). Done after the before-eval, so the baseline used the old 8-word list; all eval queries return the same listings either way.
- 2026-10-26: Criterion 5 needs 5 different queries, so a scenario's `query` may be a list; try N uses entry N (`run_eval.py::query_for`). Saves running each phrasing 5 times.
- 2026-10-26: Criterion 3 uses "black combat boots", criterion 4 uses "vintage band tee under $25" (same item every try, so only the model's wording varies).

## Open items / waiting on
- Search ranking: "black combat boots" puts a flannel shirt first (no combat boots in data; every match scores 1, ties keep file order). Logged under What's Still Broken, not fixed.
- `_search` in `agent.py` silently falls back to the direct function when MCP fails, but the trace still says "via MCP".

## Idea Shelf
