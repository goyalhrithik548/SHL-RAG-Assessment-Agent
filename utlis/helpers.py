import json
import re
from typing import Any


"""
Purpose:
This file contains small reusable helper functions.

Workflow:
Helpers are imported by services when they need text normalization, JSON
extraction, or simple display formatting.

Why this exists:
Small utilities should not live inside the main recommender class because they
are easier to reuse and debug from one shared helper file.
"""


def normalize_text(value: str) -> str:
    """
    Lowercase text and keep only letters/numbers separated by spaces.
    """
    return re.sub(
        r"[^a-z0-9]+",
        " ",
        value.lower(),
    ).strip()


def yes_no(value: bool) -> str:
    """
    Convert booleans into simple human-readable labels.
    """
    return "Yes" if value else "No"


def extract_json(text: str) -> dict[str, Any]:
    """
    Extract the first JSON object from an LLM response.

    This preserves the original regex-based behavior.
    """
    match = re.search(
        r"\{.*\}",
        text,
        flags=re.DOTALL,
    )

    if not match:
        raise ValueError("No JSON found in model output")

    return json.loads(
        match.group(0),
    )


def build_aliases(name: str) -> list[str]:
    """
    Build simple aliases for an assessment name.

    This helper is kept from the original app.py even if it is not currently
    used, so future compare or lookup work can reuse it.
    """
    words = re.findall(
        r"[A-Za-z0-9]+",
        name,
    )

    aliases = {
        normalize_text(name),
    }

    if words:
        aliases.add(
            words[0].lower(),
        )

    acronym = "".join(
        word[0].lower()
        for word in words
        if word
    )

    if len(acronym) >= 2:
        aliases.add(acronym)

    return list(aliases)
