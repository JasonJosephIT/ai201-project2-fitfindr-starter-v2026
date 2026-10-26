# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- Three or four sentences: what a user asks for, and what they get back. -->

FitFindr is a thrift-shopping helper. You type what you're looking for in plain words, like "vintage graphic tee under $30, size M", and it searches 40 secondhand listings from Depop, Poshmark and thredUp, keeping only items in your size and under your price. It picks the best match and suggests one or two outfits built from clothes already in your wardrobe. Then it writes a short, social-post-style caption (a "fit card") for the find. If nothing matches, it stops and tells you what to change: broader words, a different size or a higher price.



---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Finds listings in `data/listings.json` that match the description's keywords, after filtering out anything over the price ceiling or in the wrong size.
- **Inputs:** `description` (str), `size` (str or None — matched as whole size tokens, so "M" matches "S/M" but "S" does not match "US 9"; "One Size" listings always match), `max_price` (float or None, inclusive).
- **Returns:** A list of up to 10 (`config.SEARCH_RESULT_LIMIT`) listing dicts, best keyword match first, each with `id`, `title`, `description`, `category`, `style_tags` (list), `size`, `condition`, `price` (float), `colors` (list), `brand` (str or None) and `platform`.
- **When it has nothing:** An empty list `[]` — never None and never an exception.

### `suggest_outfit`

- **What it does:** Asks the model for one or two outfits that pair the thrifted item with pieces the user already owns.
- **Inputs:** `new_item` (dict — one listing dict from `search_listings`), `wardrobe` (dict with an `items` key holding a list of wardrobe item dicts; the list may be empty).
- **Returns:** A non-empty str of outfit suggestions, naming the wardrobe pieces exactly as they're listed.
- **When it has nothing:** If the wardrobe is empty, a str saying no fit could be found from the wardrobe, followed by an alternative fit idea. If the model returns blank text, a str saying outfit ideas couldn't be generated and to try again. It never returns `""` and never raises for an empty wardrobe.

### `create_fit_card`

- **What it does:** Writes a short caption, like a social post, about the find and how to wear it.
- **Inputs:** `outfit` (str — the output of `suggest_outfit`), `new_item` (dict — the same listing dict that went into `suggest_outfit`).
- **Returns:** A str of 2–4 sentences that names the item, its price and its platform once each and describes the vibe. The wording changes between runs (temperature 0.9).
- **When it has nothing:** If `outfit` is empty or only whitespace, a descriptive str saying there was no outfit to caption. It never returns `""` and never raises.

---

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, put a message in `session["error"]` naming what the user could change (broader words, a different size, a higher price ceiling) and stop without calling `suggest_outfit`. Otherwise, put the first result in `session["selected_item"]` and go to `suggest_outfit`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regex, in `agent.py::parse_query`. One pattern pulls a price ceiling out of "under $30", "$30", "max $30", "below $30" or "up to $30"; another pulls a size from "size M", "size US 9", "size W30" or a trailing ", M". Whatever is left becomes the search description. I chose regex over a model call because it's free, gives the same answer every time (criterion 3 depends on that), and when it's wrong I can read why in the pattern. The cost: phrasing it has never seen, like "nothing over thirty dollars", parses to no price at all, and the ceiling is silently ignored.

**What moves through the session:** In order: `query` (what the user typed) → `parsed` (description, size, max_price from parse_query) → `search_results` (everything search_listings returned) → `selected_item` (search_results[0], the one listing every later tool gets) → `outfit_suggestion` (what suggest_outfit returned) → `fit_card` (what create_fit_card returned). `wardrobe` is put in at the start and only read. `error` stays None unless the run stops early: on an empty search it holds the "what to change" message, and if the model can't be reached it says so and keeps the search results.

---

## Sample Run

<!-- Two things go here.

     1. One FULL query and its output, pasted as text.
     2. Your three per-tool terminal tests — the command and what it printed. -->

**One full query**

```
$ python app.py ask 'vintage graphic tee under $30'

  Found:    Y2K Baby Tee — Butterfly Print — $18.0 on depop

  Outfit:   Outfit 1: Lean into the Y2K aesthetic by pairing the baby tee with the baggy straight-leg jeans, dark wash. Cinch the waist with the brown leather belt, and finish the look with the chunky white sneakers and the black crossbody bag.

Outfit 2: Balance the fitted, cropped tee with the wide-leg khaki trousers. Layer the vintage black denim jacket on top and lace up the black combat boots to add a little edge to the pastel butterfly print.

  Fit card: Found this sweet little butterfly tee on depop for just 18 bucks and I'm obsessed. I've been styling it with baggy dark denim and chunky sneakers for the ultimate early 2000s mallrat energy. But it also looks so good toughened up with wide-leg khakis and combat boots.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print([(l['title'], l['price'], l['size']) for l in search_listings('graphic tee', max_price=30)])"
[('Y2K Baby Tee — Butterfly Print', 18.0, 'S/M'), ('Graphic Tee — 2003 Tour Bootleg Style', 24.0, 'L'), ('Mesh Long-Sleeve Top — Black', 15.0, 'S/M'), ('Vintage Band Tee — Faded Grey', 19.0, 'L'), ('Low-Rise Cargo Pants — Khaki', 27.0, 'W29'), ('Vintage Graphic Hoodie — Faded Black', 26.0, 'L')]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
Outfit 1:
Pair the vintage Levi's 501s with the white ribbed tank top tucked in, cinched at the waist with the brown leather belt. Layer the slightly cropped vintage black denim jacket on top, and finish the look with the chunky white sneakers and black crossbody bag for an effortless, casual streetwear vibe.

Outfit 2:
Style the Levi's 501s with the oversized grey crewneck sweatshirt draped loosely over the top. Slip into the black combat boots, and throw the black cropped zip hoodie layered underneath or over your shoulders for a cozy, texture-rich outfit that lets the knee-fading of the vintage jeans stand out.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
Scored these vintage Levi's 501s on Depop for $38 and they fit like an absolute dream. Threw them on with some beat-up white sneakers for that effortless 90s dad running errands vibe. Honestly never taking these off.
```

---

## How I Used AI

<!-- Two specific moments. What you asked, what came back, what you changed.

     "I used Claude to help me code" is not enough.

     "I gave Claude my search_listings spec. It returned None on no match
     instead of an empty list, so I changed it" is the level we want. -->

**Moment 1**

- *What I asked for:* I asked Claude to finish the stopword list in `tools.py` (`_STOPWORDS`), which only had 8 words ("a", "the", "for"…), so filler in a query stops counting as a keyword match.
- *What came back:* About 80 words in three groups: grammar words ("or", "but", "to"), request filler ("looking", "something", "cute") and price/size words the parser can leave behind ("under", "bucks", "size"). It checked old against new: every eval query returned the same listings, but "boots size 9" went from 6 matches to 1, because "size" had been matching any listing that mentions a size.
- *What I changed:* I had it add 15 more everyday words ("were", "have", "would", "what", "which"…), bringing the list to 100, so question-style queries like "what jacket would go with jeans" only match on "jacket" and "jeans".

**Moment 2**

- *What I asked for:* After criterion 4 missed (two fit cards said "twenty-four bucks" instead of "$24"), I first asked Claude to loosen the criterion to accept "bucks" or "dollars". Then I asked whether the price in the card was produced deterministically or by the model.
- *What came back:* It wrote the revision but warned that loosening a criterion right after missing it is what the rubric calls lowering a target. On the second question: the code builds "$24" from the listing, but the model writes the caption freely and nothing checks it. It proposed a check in `create_fit_card`: if the exact price isn't in the caption, retry once, then append "($24 on depop.)".
- *What I changed:* I took the code fix and dropped the criterion revision, so criterion 4 stays as written in unit 3 and the before-run still counts as a miss.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item search found is the item every later tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card is a short post that names the price and platform | 4 of 5 | FAIL | FAIL | PASS | PASS | PASS | MISSED (3/5) |
| 5. Search never returns anything above the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
Criterion 4, try 1 — `tools.py::create_fit_card`, from results/run_2026-10-26_0031_before.md
Item: Graphic Tee — 2003 Tour Bootleg Style ($24.0, depop)

scored this bootleg tour tee on depop for twenty-four bucks and I'm obsessed. figured out two ways to style it today, from heavy grunge with combat boots to a relaxed streetwear vibe in khakis. honestly might live in this shirt all fall.
```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 | A matching query completes all three tools | 4 of 5 | MET (5/5) | Every try ended with `session["error"]` = None and a fit card set; the trace shows all three tools ran. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET (5/5) | Every trace ends at step 3, "branch", with no suggest_outfit step, and the error names the description, size and price to change. |
| 3 | The item search found is the item every later tool received | 5 of 5 | MET (5/5) | In every trace the first search result, `selected_item`, and the input to suggest_outfit and create_fit_card are the same listing. The report prints titles, not ids; all 40 titles are unique, so same title means same id. |
| 4 | The fit card names the price and platform | 4 of 5 | MISSED (3/5) | Searched each card for "$24" and "depop" and counted sentences and words. Tries 1 and 2 wrote the price as "twenty-four bucks" / "twenty four bucks"; all five were 3 sentences or fewer and under 80 words. |
| 5 | Search never returns anything above the price ceiling | 5 of 5 | MET (5/5) | For all five phrasings `parsed["max_price"]` equals the typed number, and re-running the same parse and search shows no result above it (highest: $27 of 30, $45 of 50, $32 of 35). |

**Diagnoses**

Criterion 4 missed in the model's output, not in a tool, the loop or the session. `create_fit_card` builds the price exactly ("$24") from the listing and puts it in the prompt twice, but at temperature 0.9 the model is writing a casual social post, and people write "24 bucks". Nothing after `generate()` checked the caption, so the model's rewording went straight to the user. The tool did its job; it trusted the model to copy a fact it was free to rephrase. Both misses are the same problem: one item, the same mechanism.

---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
$ python app.py ask 'vintage graphic tee under $30' --trace
[1] parse_query
      in:  vintage graphic tee under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style, Vintage Band Tee — Faded Grey … +7 more
      →    10 match(es)
[3] select_item
      out: Y2K Baby Tee — Butterfly Print ($18.0, depop)
[4] suggest_outfit
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Outfit 1: Lean into the Y2K aesthetic by pairing the baby tee with the baggy straight-leg jeans, dark wash. Ci…
      →    10 wardrobe item(s)
[5] create_fit_card
      in:  Y2K Baby Tee — Butterfly Print ($18.0, depop)
      out: Found this sweet little butterfly tee on depop for just 18 bucks and I'm obsessed. I've been styling it with b…
```

**Empty search**

```
$ python app.py ask 'designer ballgown size XXS under $5' --trace
[1] parse_query
      in:  designer ballgown size XXS under $5
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
      →    0 match(es)
[3] branch
      →    search returned []: stopping before suggest_outfit
```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->

`search_listings` is registered as a tool in `mcp_server.py` with `@mcp.tool()`, wrapping the real implementation imported under an alias so it doesn't call itself. In `agent.py`, `run_agent` now calls it through `_search`, which uses `mcp_client.call_tool("search_listings", {...})`. Nothing behaved differently afterwards: called directly over MCP, "graphic tee" under $30 returns the same 6 listings as before, still as a list of dicts with float prices. One weak spot: if the MCP call fails, `_search` quietly falls back to the direct function, and the trace still says "via MCP". The run works, but the label can be wrong.



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:** In `tools.py::create_fit_card`, after the model replies, the code checks that the exact price string (e.g. "$24") is in the caption. If it isn't, it calls the model once more; if the retry still drops it, it appends "($24 on depop.)" to the first caption. The price now comes from the listing, not from the model's wording.

**Which failure it was meant to fix:** Criterion 4: two of five cards gave the price as "twenty-four bucks", so the price wasn't stated in a form anyone could check.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The item search found is the item every later tool received | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 4. The fit card is a short post that names the price and platform | 4 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 5. Search never returns anything above the price ceiling | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:** Yes for criterion 4: 3/5 before, 5/5 after (results/run_2026-10-26_0041_after.md). All five cards said "$24" and "depop", were 3 sentences, and ran 52–65 words. None of them carry the appended "($24 on depop.)", so either the model wrote "$24" the first time or the retry fixed it. The run made 50 model calls against 41 before, which fits a few retries, but the log doesn't record retries, so I can't say how many. Nothing else changed: criteria 1, 2, 3 and 5 stayed at 5/5.

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->

- **Criterion 5 passed partly on empty results.** "boots max $40" and "hoodie up to $25" found nothing: the only boots are $44 and the only hoodie is $26. An empty list can't break a ceiling, so 2 of the 5 tries tested the parser but not the filter. Next I'd swap them for phrasings that match something, e.g. "boots max $50".
- **Search ranks weak matches first.** "black combat boots" put an Oversized Flannel Shirt first. There are no combat boots in the data, so every listing scored 1 on a single word ("black" or "boots"), and ties keep the file's order. The Suede Chelsea Boots tie with the flannel and lose on order. Criterion 3 still passed because it checks the hand-off, not whether the pick was good. A fix would weight title and category matches above description matches.
- **Spelled-out prices aren't parsed.** "nothing over thirty dollars" sets no ceiling, and the search quietly ignores it. Known since unit 3; it would need a number-word step in `parse_query`.
- **The trace can claim MCP when it didn't happen.** If the MCP call fails, `agent.py::_search` falls back to the direct function, and the step still says "search_listings (via MCP)".
- **Retries are invisible.** The price retry in `create_fit_card` isn't logged, so I can't tell from a run how often the model dropped the price.

I stopped at one measured change, which is what the milestone asks for.

<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
