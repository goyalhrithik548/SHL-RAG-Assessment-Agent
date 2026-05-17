from langchain_huggingface import HuggingFaceEmbeddings


"""
Purpose:
This file creates the HuggingFace embedding model used by FAISS.

Workflow:
1. Receive the embedding model name from the recommender.
2. Return a LangChain HuggingFaceEmbeddings object.

Why this exists:
Embedding setup is isolated here so model changes do not require editing the
main recommender or API route files.
"""


def get_embeddings(model_name):
    """
    Create the embedding model used for catalog vector search.
    """
    return HuggingFaceEmbeddings(
        model_name=model_name,
    )
