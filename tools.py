"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
import re
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────
_STOPWORDS = {
    # grammar words
    "a", "an", "and", "the", "for", "with", "in", "of", "or", "but", "on",
    "at", "to", "from", "by", "as", "is", "it", "its", "it's", "be", "are",
    "was", "that", "this", "these", "those", "some", "any", "very", "so",
    "can", "no", "not", "just", "too", "also", "were", "have", "has", "had",
    "do", "does", "will", "would", "could", "should", "if", "what", "which",
    "there", "into",
    # how people phrase a request
    "i", "i'm", "im", "me", "my", "we", "you", "your", "want", "wanna", "need",
    "looking", "look", "find", "show", "get", "buy", "please", "something",
    "anything", "thing", "item", "items", "piece", "one", "kind", "sort",
    "like", "good", "nice", "cute", "really",
    # price and size words parse_query can leave behind ("under 30", "size 9")
    "under", "below", "less", "than", "max", "up", "over", "around",
    "about", "price", "dollars", "dollar", "bucks", "cheap", "size", "sized",
}

def _keywords(text: str) -> set[str]:
    """Lowercase words worth matching on, stopwords removed."""
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}

def _size_tokens(size: str) -> set[str]:
    cleaned = re.sub(r"\([^)]*\)", " ", size or "") # drop parentheticals
    parts = [p.strip().upper() for p in cleaned.split("/")]
    return {p for p in parts if p}

def _size_matches(wanted: str, listing_size: str) -> bool:
    if not wanted:
        return True
    listing_tokens = _size_tokens(listing_size)
    if any(token.startswith("ONE SIZE") for token in listing_tokens):
        return True
    return bool(_size_tokens(wanted) & listing_tokens)

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.

    TODO:
        1. Load every listing with load_listings().
        2. Filter by max_price and by size, when each is provided.
        3. Score what's left by keyword overlap with `description`.
        4. Drop anything scoring zero.
        5. Sort by score, highest first, and return the listing dicts —
           at most config.SEARCH_RESULT_LIMIT of them.

    Test it from a terminal before you move on:
        python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"
    """
    # 1. Load every listing.
    listings = load_listings()

    # 2. Filter by price and size, skipping whichever wasn't given.
    if max_price is not None:
        listings = [l for l in listings if l["price"] <= max_price]
    if size:
        listings = [l for l in listings if _size_matches(size, l["size"])]

    # 3. Score each listing by how many query keywords appear in its text.
    query = _keywords(description)
    scored = []
    for l in listings:
        text = " ".join([
            l["title"],
            l["description"],
            l["category"],
            " ".join(l.get("style_tags") or []),
            " ".join(l.get("colors") or []),
            l.get("brand") or "",
        ])
        scored.append((len(query & _keywords(text)), l))

    # 4. Drop anything with no keyword in common.
    scored = [(score, l) for score, l in scored if score > 0]

    # 5. Best match first, capped at the result limit. sorted() is stable, so
    #    ties keep the data file's order and the same query gives the same list.
    scored = sorted(scored, key=lambda pair: pair[0], reverse=True)
    return [l for _, l in scored[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def _alt_fit_suggestion(new_item: dict) -> str:
    """
    General styling advice for when the wardrobe is empty.

    Built from the item's own fields rather than a model call, so the empty
    wardrobe path still answers when the model can't be reached.
    """
    title = new_item.get("title", "this item")
    colors = new_item.get("colors") or []
    color_note = (
        f"Let the {colors[0]} be the focus and keep everything else neutral — "
        if colors else "Keep everything around it neutral — "
    )
    # staples that fill the gaps around the item, never a second of the same thing
    staples = {
        "tops": "straight-leg jeans and clean white sneakers",
        "bottoms": "a plain white or black tee and clean white sneakers",
        "outerwear": "a plain tee, straight-leg jeans and clean white sneakers",
        "shoes": "straight-leg jeans and a plain white or black tee",
    }.get(new_item.get("category"), "a plain tee, straight-leg jeans and clean white sneakers")
    return (
        f"build the look around {title} with staples most closets start with: "
        f"{staples}. {color_note}black, white, grey, denim or tan. Add your "
        f"own pieces to the wardrobe for outfits built from what you own."
    )


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, say no fit could be found and offer an
        alternative fit from _alt_fit_suggestion() instead — never raise or
        return "". Unit 4 triggers this on purpose.

    TODO:
        1. Check whether wardrobe['items'] is empty.
        2. If it is, say no fit was found and return _alt_fit_suggestion().
        3. If it isn't, format the wardrobe items into the prompt and ask for
           specific combinations naming pieces the user already owns.
        4. Return the model's response.

    Test it from a terminal before you move on:
        python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
    """
    items = (wardrobe or {}).get("items") or []

    # brand is None on most listings, so only mention it when it's there
    item_desc = (
        f"{new_item.get('title', 'Unnamed item')}"
        f"{' by ' + new_item['brand'] if new_item.get('brand') else ''}"
        f" — {new_item.get('category', 'unknown category')}, "
        f"colors: {', '.join(new_item.get('colors') or []) or 'unspecified'}, "
        f"style: {', '.join(new_item.get('style_tags') or []) or 'unspecified'}. "
        f"{new_item.get('description', '')}"
    )

    system = (
        "You are a thrift-savvy personal stylist. Give concrete, wearable outfit "
        "ideas in plain text. Suggest one or two outfits, a few lines each."
    )

    if not items:
        return (
            f"I couldn't find a fit for {new_item.get('title', 'this item')} "
            f"from your wardrobe. Here's an alternative fit instead: "
            f"{_alt_fit_suggestion(new_item)}"
        )

    wardrobe_lines = "\n".join(
        f"- {w.get('name', 'Unnamed')} ({w.get('category', '?')}; "
        f"colors: {', '.join(w.get('colors') or []) or 'unspecified'}"
        f"{'; notes: ' + w['notes'] if w.get('notes') else ''})"
        for w in items
    )
    prompt = (
        f"Someone is considering this thrifted piece:\n{item_desc}\n\n"
        f"Here is what they already own:\n{wardrobe_lines}\n\n"
        "Suggest one or two specific outfits pairing the new piece with "
        "items from their wardrobe. Name the wardrobe pieces exactly as "
        "listed above, and only use pieces they actually own."
    )

    response = generate(prompt, system=system)
    if not response.strip():
        return (
            f"Couldn't generate outfit ideas for {new_item.get('title', 'this item')} "
            "right now — try again in a moment."
        )
    return response


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.

    It should also come out **differently for different inputs**. If you run
    this three times on the same item and get three word-for-word identical
    strings, it's one of two things, and both are near the top of `config.py`:

        • CACHE_ENABLED — the adapter handed back an answer it already had
        • TEMPERATURE   — at 0.0 the model gives the same words every time

    TODO:
        1. Guard against an empty or whitespace-only `outfit`.
        2. Build a prompt with the item details and the outfit.
        3. Call generate() and return the response.

    Test it from a terminal before you move on:
        python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
    """
    title = new_item.get("title", "this item")

    # 1. Nothing to caption — say so rather than asking the model to invent one.
    if not (outfit or "").strip():
        return f"No outfit was suggested for {title}, so there's no fit card to write."

    # 2. The facts the caption has to get right, given once each.
    price = new_item.get("price")
    price_text = f"${price:g}" if isinstance(price, (int, float)) else "an unlisted price"
    platform = new_item.get("platform") or "a resale app"
    brand = f" by {new_item['brand']}" if new_item.get("brand") else ""

    system = (
        "You write short social captions for thrift finds. Sound like a real "
        "person posting a fit, not a product listing. Plain text, no hashtags."
    )
    prompt = (
        f"The find: {title}{brand}, {price_text} on {platform}, "
        f"condition: {new_item.get('condition', 'unknown')}.\n"
        f"How it's being styled:\n{outfit}\n\n"
        f"Write a 2 to 4 sentence caption. Mention the item, the price "
        f"({price_text}) and the platform ({platform}) once each, and be "
        f"specific about the vibe of the outfit."
    )

    # 3. Call the model; a blank answer still gets a sentence, not "".
    response = generate(prompt, system=system)
    if not response.strip():
        return f"Couldn't write a fit card for {title} right now — try again in a moment."

    return response.strip()
