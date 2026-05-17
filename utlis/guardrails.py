from utils.constants import INJECTION_PATTERNS


"""
Purpose:
This file contains simple safety checks for chat input.

Workflow:
1. Check the latest user message for prompt-injection phrases.
2. Check fallback-routing text for obvious off-topic words.

Why this exists:
Guardrails are easier to maintain when they are separate from routing,
recommendation generation, and API code.
"""


def contains_prompt_injection(text: str) -> bool:
    """
    Return True when the latest user message contains a blocked phrase.
    """
    lowered = text.lower()

    for pattern in INJECTION_PATTERNS:
        if pattern in lowered:
            return True

    return False


def contains_off_topic(
    text: str,
    off_topic_words: list[str],
) -> bool:
    """
    Return True when fallback routing sees an off-topic keyword.
    """
    lowered = text.lower()

    return any(
        word in lowered
        for word in off_topic_words
    )
