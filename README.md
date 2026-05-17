# SHL Assessment Recommender

This is a simple, beginner-friendly submission for the SHL AI Intern assignment.

It uses:

- `FastAPI` for the backend API
- `Streamlit` for the demo chat UI
- `LangChain` for prompt and LLM wiring
- `FAISS` for catalog retrieval
- `Groq` for the chat model
- Cached SHL assessment catalog data for recommendations

## Project structure

The backend has been split into small files so each part is easier to debug.

```text
project/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── .env
├── api/
│   ├── routes.py
│   └── models.py
├── services/
│   ├── recommender.py
│   ├── routing_service.py
│   ├── recommendation_service.py
│   └── memory_service.py
├── rag/
│   ├── vector_store.py
│   ├── embeddings.py
│   └── retriever.py
├── scraper/
│   └── catalog_loader.py
├── utils/
│   ├── helpers.py
│   ├── constants.py
│   └── guardrails.py
└── data/
    └── catalog_cache.json
```

## File responsibilities

- `app.py` - small FastAPI entry point that creates the app and includes routes.
- `api/models.py` - Pydantic request and response models.
- `api/routes.py` - FastAPI endpoints: `GET /health` and `POST /chat`.
- `services/recommender.py` - main orchestration for memory, routing, retrieval, and recommendations.
- `services/routing_service.py` - decides whether to clarify, recommend, compare, or refuse.
- `services/recommendation_service.py` - formats FAISS search results into API recommendations.
- `services/memory_service.py` - rebuilds stateless conversation memory from request messages.
- `rag/vector_store.py` - builds the FAISS vector store from catalog entries.
- `rag/embeddings.py` - creates the HuggingFace embedding model.
- `rag/retriever.py` - performs similarity search against FAISS.
- `scraper/catalog_loader.py` - loads the cached SHL catalog JSON.
- `utils/helpers.py` - shared helpers such as `normalize_text` and `extract_json`.
- `utils/constants.py` - shared URLs, labels, paths, and keyword lists.
- `utils/guardrails.py` - prompt-injection and off-topic checks.
- `streamlit_app.py` - demo frontend that calls the FastAPI backend.

## How it works

1. FastAPI starts from `app.py`.
2. The shared recommender loads the cached catalog from `data/catalog_cache.json`.
3. The catalog is converted into LangChain documents.
4. FAISS is built using HuggingFace embeddings.
5. On each `POST /chat`, the backend rebuilds memory from the stateless message history.
6. The routing service decides whether the assistant should clarify, recommend, compare, or refuse.
7. If recommendations are needed, FAISS searches the SHL catalog and returns matching assessments.
8. The response keeps the same API schema used by the Streamlit frontend.

## Setup

Python `3.11` or `3.12` is recommended for the smoothest FAISS experience.

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your Groq key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_URL=http://127.0.0.1:8000
```

## Run the FastAPI app

```bash
uvicorn app:app --reload
```

Endpoints:

- `GET /health`
- `POST /chat`

## Run the Streamlit demo

Start the API first, then run:

```bash
streamlit run streamlit_app.py
```

## Example request

```json
{
  "messages": [
    {
      "role": "user",
      "content": "I am hiring a mid-level Java developer who works with stakeholders."
    }
  ]
}
```

## Notes

- The API is stateless, as required by the assignment.
- Recommendations come from cached SHL catalog records.
- `data/catalog_cache.json` is the preferred cache location.
- The root-level `catalog_cache.json` is still supported as a fallback.
- The public API schema and Streamlit request format remain unchanged.
