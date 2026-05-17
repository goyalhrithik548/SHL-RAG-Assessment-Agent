from api.models import ChatResponse, Recommendation
from rag.retriever import retrieve_candidates


"""
Purpose:
This file turns a conversation into SHL assessment recommendations.

Workflow:
1. Search the FAISS vector store for matching catalog entries.
2. Convert the top matches into API response models.
3. Return the same ChatResponse shape used by the original app.py.

Why this exists:
Recommendation formatting is easier to test and debug when it is separate from
routing and FastAPI endpoint code.
"""


def recommend(
    vector_store,
    history_text,
):
    """
    Create a recommendation response from the conversation history.

    The number of searched candidates and returned recommendations matches the
    original implementation.
    """
    candidates = retrieve_candidates(
        vector_store=vector_store,
        query=history_text,
        limit=10,
    )

    recommendations = format_recommendations(
        candidates,
    )

    return ChatResponse(
        reply=(
            f"Here are {len(recommendations)} "
            "SHL assessments that match your requirements."
        ),
        recommendations=recommendations,
        end_of_conversation=False,
    )


def format_recommendations(candidates):
    """
    Convert LangChain Documents into Recommendation models.

    Only the first five results are returned, preserving the old behavior.
    """
    recommendations = []

    for doc in candidates[:5]:
        recommendations.append(
            Recommendation(
                name=doc.metadata["name"],
                url=doc.metadata["url"],
                test_type=doc.metadata["test_type"],
            ),
        )

    return recommendations
