"""
The runs your test needs. ← UNIT 4, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
the empty-search branch needs an impossible query. One about the fit card needs
the same item run more than once. Working that out is Milestone 3's first step,
and this file is where you write it down.

`run_eval.py` runs everything here five times and writes the run log — five
because your criteria are written out of five.

Three scenarios are filled in to show the shape. Add or change whatever your
own criteria need — these are a starting point, not a fixed set.
"""

SCENARIOS = [
    {
        # A query the data can match. Criterion 1.
        "name": "matching query completes",
        "query": "vintage graphic tee under $30",
        "wardrobe": "example",
        "criterion": 1,
    },
    {
        # A query nothing can match. Criterion 2 — the branch.
        "name": "impossible query stops early",
        "query": "designer ballgown size XXS under $5",
        "wardrobe": "example",
        "criterion": 2,
    },
    {
        # A user with nothing saved. One of unit 4's three failure modes.
        "name": "empty wardrobe",
        "query": "denim jacket under $50",
        "wardrobe": "empty",
        "criterion": None,
    },
    {
        # Criterion 3 — the selected item's id survives every hand-off.
        "name": "selected item is passed through unchanged",
        "query": "black combat boots",
        "wardrobe": "example",
        "criterion": 3,
    },
    {
        # Criterion 4 — same item each try, so only the model's wording varies.
        "name": "fit card names price and platform",
        "query": "vintage band tee under $25",
        "wardrobe": "example",
        "criterion": 4,
    },
    {
        # Criterion 5 — five phrasings of a ceiling, one per try.
        "name": "search respects the price ceiling",
        "query": [
            "graphic tee under $30",
            "denim jacket $50",
            "boots max $40",
            "cargo pants below $35",
            "hoodie up to $25",
        ],
        "wardrobe": "example",
        "criterion": 5,
    },
]

WARDROBES = ("example", "empty")


def validate() -> list[str]:
    """Complain about anything malformed, before a long run rather than during."""
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        queries = scenario.get("query") or ""
        if isinstance(queries, str):
            queries = [queries]
        if not all(q.strip() for q in queries):
            problems.append(f"scenario {i} has no query")
        if scenario.get("wardrobe") not in WARDROBES:
            problems.append(
                f"scenario {i} has wardrobe {scenario.get('wardrobe')!r} — "
                f"it should be one of {WARDROBES}"
            )
    return problems
