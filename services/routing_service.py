from langchain_core.prompts import ChatPromptTemplate

from utils.constants import (
    OFF_TOPIC_WORDS,
    ROLE_KEYWORDS,
    SENIORITY_KEYWORDS,
    SKILL_FOCUS_KEYWORDS,
)
from utils.guardrails import contains_off_topic
from utils.helpers import extract_json


"""
Purpose:
This file decides what kind of conversation turn we are handling.

Workflow:
1. Ask the LLM to classify the request as clarify, recommend, compare, or refuse.
2. If the LLM call or JSON parsing fails, use simple keyword fallback logic.
3. Return a small dictionary with action and reply.

Why this exists:
Routing is easier to debug when it is separate from FAISS retrieval and FastAPI
endpoint code.
"""


def route_request(
    history_text,
    last_user_message,
    get_llm,
):
    """
    Decide whether to clarify, recommend, compare, or refuse.

    get_llm is a small callback from SHLRecommender. It keeps Groq setup in one
    place while letting this file focus on routing.
    """
    route_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a conversational SHL assessment assistant.

Rules:
- Stay inside SHL assessments only
- Ask clarification questions before recommending
- Compare assessments when asked
- Refuse off-topic questions
- Only recommend when enough detail exists

Return ONLY valid JSON.

Format:

{
 "action":"clarify|recommend|compare|refuse",
 "reply":"assistant reply"
}
                """,
            ),
            (
                "human",
                """
Conversation:
{history_text}

Last user message:
{last_user_message}
                """,
            ),
        ],
    )

    # Preserve the original behavior: missing GROQ_API_KEY should raise here.
    llm = get_llm()

    try:
        response = (
            route_prompt | llm
        ).invoke(
            {
                "history_text": history_text,
                "last_user_message": last_user_message,
            },
        )

        parsed = extract_json(response.content)

        if "action" not in parsed:
            raise ValueError("Missing action")

        return parsed

    except Exception:
        # If the LLM response is not usable, fallback rules keep the app working.
        return fallback_route(history_text)


def fallback_route(history_text):
    """
    Keyword-based backup routing used when the LLM output cannot be parsed.

    The checks below are intentionally simple and mirror the original app.py.
    """
    lowered = history_text.lower()

    # Compare requests.
    if (
        "compare" in lowered
        or "difference" in lowered
        or "vs" in lowered
    ):
        return {
            "action": "compare",
            "reply": "Sure, I can compare those SHL assessments.",
        }

    # Refuse off-topic requests.
    if contains_off_topic(lowered, OFF_TOPIC_WORDS):
        return {
            "action": "refuse",
            "reply": (
                "I can only help with SHL assessments "
                "and hiring-related recommendations."
            ),
        }

    # Check whether the user has described the role.
    has_role = any(
        word in lowered
        for word in ROLE_KEYWORDS
    )

    # Check whether the user has described experience level.
    has_seniority = any(
        word in lowered
        for word in SENIORITY_KEYWORDS
    )

    # Check whether the user has described assessment focus.
    has_skill_focus = any(
        word in lowered
        for word in SKILL_FOCUS_KEYWORDS
    )

    # Missing role.
    if not has_role:
        return {
            "action": "clarify",
            "reply": "What type of role are you hiring for?",
        }

    # Missing seniority.
    if not has_seniority:
        return {
            "action": "clarify",
            "reply": (
                "What seniority level or years of experience "
                "are you hiring for?"
            ),
        }

    # Missing skill focus.
    if not has_skill_focus:
        return {
            "action": "clarify",
            "reply": (
                "Are you looking for technical, personality, "
                "cognitive, leadership, or communication assessments?"
            ),
        }

    # Enough detail.
    return {
        "action": "recommend",
        "reply": (
            "Thanks. I now have enough information "
            "to recommend suitable SHL assessments."
        ),
    }
