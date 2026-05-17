"""
Purpose:
This file contains the similarity-search step.

Workflow:
1. Receive the FAISS vector store.
2. Search it with the conversation text.
3. Return matching LangChain Documents.

Why this exists:
Keeping retrieval separate makes it easy to debug whether problems come from
search, recommendation formatting, or routing.
"""


def retrieve_candidates(
    vector_store,
    query,
    limit=10,
):
    """
    Search FAISS for the most relevant catalog documents.
    """
    return vector_store.similarity_search(
        query,
        k=limit,
    )
