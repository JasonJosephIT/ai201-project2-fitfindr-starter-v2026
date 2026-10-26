# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
Search is deterministic, but the two steps after it call the model through a
rate-limited free tier (15 requests a minute), so one run in five can hit a
retry ceiling or come back empty and end with `session["error"]` set instead of
a card. 5 of 5 would be grading the network; anything below 4 of 5 would mean
my own loop is dropping runs.

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
This path never touches the model: `parse_query` is regex, `search_listings`
is a keyword filter over a fixed 40-listing file, and the branch is a plain
`if not results`. Same input, same output, every time — so a single miss is a
bug in my branch, not noise, and anything under 5 of 5 should fail.

---

## 3. The item search found is the item every later tool received

On a matching query, the `id` of `session["selected_item"]` equals the `id` of
`session["search_results"][0]`, and the trace shows that same `id` as the input
to both `suggest_outfit` and `create_fit_card` — in 5 of 5 tries.

**Why this target:**
Handing the item from one step to the next is ordinary Python, with no model
and no randomness involved — the only way it breaks is if my code overwrites or
rebuilds the dict between steps (for example, the MCP path returning a
re-serialized copy). That kind of bug is deterministic, so it would show up
every time; 5 of 5 is the only target that catches it instead of excusing it.

---

## 4. The fit card is a short post that names the price and platform

For a matching query, the fit card is 2–4 sentences, under 80 words, and
contains both the item's price (e.g. `$24`) and its platform name (`depop`,
`poshmark` or `thredUp`, case-insensitive) — in at least 4 of 5 tries.

**Why this target:**
The card is written by a small model at temperature 0.9, so the wording is
supposed to vary and occasionally it will drop a detail or run long even when
the prompt asks for both. Price and platform are the two facts a buyer actually
needs and they're checkable with a string match, so they're what I score. 4 of
5 allows one model slip; 3 of 5 would mean my prompt isn't doing its job.

---

## 5. Search never returns anything above the price ceiling

For every query that includes a price ceiling (e.g. "under $30"), every listing
in `session["search_results"]` has `price <= max_price`, and
`session["parsed"]["max_price"]` equals the number the user typed — across 5
different queries, 5 of 5.

**Why this target:**
A thrifter who says "under $30" and gets a $45 jacket stops trusting the app,
so this matters more than any wording. Both the regex that pulls the price out
and the filter in `search_listings` are deterministic, so there's no excuse
for a miss. The 5 queries vary the phrasing ("under $30", "$30", "max $30") so
the target tests the parser, not just the filter — phrasings like "nothing over
thirty dollars" are a known gap and are deliberately left out.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
