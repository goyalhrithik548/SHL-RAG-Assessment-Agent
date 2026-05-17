from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from rag.embeddings import get_embeddings


"""
Purpose:
This file builds the FAISS vector store from the SHL catalog.

Workflow:
1. Convert each catalog item into a LangChain Document.
2. Attach useful metadata for the API response.
3. Build a FAISS index with HuggingFace embeddings.

Why this exists:
FAISS setup is a RAG concern, so it lives in rag/ instead of the FastAPI app or
the recommendation orchestration class.
"""


def build_vector_store(
    catalog,
    embedding_model_name,
):
    """
    Build a FAISS vector store from catalog entries.

    The page_content and metadata match the original implementation.
    """
    documents = build_documents(
        catalog,
    )

    embeddings = get_embeddings(
        embedding_model_name,
    )

    return FAISS.from_documents(
        documents,
        embeddings,
    )


def build_documents(catalog):
    """
    Convert raw catalog dictionaries into LangChain Documents.

    These documents are what FAISS searches over.
    """
    documents = []

    for item in catalog:
        page_content = "\n".join(
            [
                f"Assessment Name: {item['name']}",
                f"Description: {item.get('description')}",
                f"Job Levels: {item.get('job_levels')}",
                f"Languages: {item.get('languages')}",
                f"Assessment Length: {item.get('assessment_length')}",
                f"Catalog URL: {item['url']}",
            ],
        )

        documents.append(
            Document(
                page_content=page_content,
                metadata={
                    "name": item["name"],
                    "url": item["url"],
                    "test_type": item["test_type"],
                },
            ),
        )

    return documents
