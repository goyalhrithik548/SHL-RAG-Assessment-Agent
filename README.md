# Conversational SHL Assessment Recommender

FastAPI + LangChain + FAISS + Groq based conversational recommender for the SHL AI Intern assignment.

The system helps a recruiter or hiring manager move from a vague hiring need to a shortlist of SHL assessments. It asks clarification questions when needed, uses the cached SHL catalog for retrieval, refuses off-topic or prompt-injection requests, and returns the exact stateless API schema required by the assignment.

## Assignment Goal

The assignment asks for a conversational SHL assessment recommender that can:

- Use the SHL product catalog for Individual Test Solutions.
- Expose a FastAPI service.
- Provide `GET /health`.
- Provide `POST /chat`.
- Accept full stateless conversation history in every chat request.
- Clarify vague requests before recommending.
- Recommend catalog-backed SHL assessments when enough context exists.
- Refine recommendations when the user changes constraints.
- Handle comparison-style requests.
- Refuse off-topic or prompt-injection attempts.
- Return only URLs that come from the SHL catalog data.

## Tech Stack

- `FastAPI` for the backend API.
- `Streamlit` for local frontend testing.
- `LangChain` for prompt and LLM workflow.
- `FAISS` for vector search.
- `HuggingFaceEmbeddings` for embedding catalog text.
- `Groq` for LLM-based routing.
- `Pydantic` for request and response validation.
- `Railway` for deployment.

## Actual Project Structure

```text
SHL Assignment/
├── app.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── .env
├── SHL_AI_Intern_Assignment.pdf
├── catalog_cache.json
├── api/
│   ├── models.py
│   └── routes.py
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
│   ├── constants.py
│   ├── guardrails.py
│   └── helpers.py
└── data/
    ├── catalog_cache.json
    └── shl_catalog.csv
```

Generated folders such as `__pycache__/` and local folders such as `.venv/` are not part of the source code. The `.env` file is for local development secrets and should not be committed publicly.

## File Responsibilities

### `app.py`

Small FastAPI entry file.

It creates the FastAPI app, initializes the recommender on startup, and includes the API routes from `api/routes.py`.

### `api/models.py`

Contains all Pydantic models:

- `Message`
- `ChatRequest`
- `Recommendation`
- `ChatResponse`

This file protects the assignment API schema from accidental changes.

### `api/routes.py`

Contains only FastAPI routes:

- `GET /health`
- `POST /chat`

The route file keeps HTTP handling separate from recommendation logic.

### `services/recommender.py`

Main orchestration service.

It loads the catalog, builds the FAISS vector store, rebuilds stateless memory, checks guardrails, routes the conversation, and calls the recommendation service.

### `services/routing_service.py`

Decides the next conversational action:

- `clarify`
- `recommend`
- `compare`
- `refuse`

It uses Groq through LangChain and has fallback keyword logic if the model output cannot be parsed.

### `services/recommendation_service.py`

Turns FAISS search results into structured API recommendations.

It returns catalog-backed assessment names, URLs, and test types.

### `services/memory_service.py`

Rebuilds conversation memory from the request messages.

The backend is stateless, so it does not store per-user sessions.

### `rag/vector_store.py`

Builds the FAISS index from catalog records.

Each catalog item is converted into a LangChain document containing assessment name, description, job levels, languages, assessment length, and catalog URL.

### `rag/embeddings.py`

Creates the HuggingFace embedding model.

Default:

```text
sentence-transformers/all-MiniLM-L6-v2
```

### `rag/retriever.py`

Runs similarity search against the FAISS vector store.

### `scraper/catalog_loader.py`

Loads the cached catalog JSON.

Preferred path:

```text
data/catalog_cache.json
```

Fallback path:

```text
catalog_cache.json
```

### `utils/constants.py`

Stores shared constants such as catalog URLs, cache paths, prompt-injection patterns, test type labels, and fallback routing keywords.

### `utils/guardrails.py`

Contains prompt-injection and off-topic checks.

### `utils/helpers.py`

Contains small helper functions such as:

- `normalize_text`
- `extract_json`
- `yes_no`
- `build_aliases`

### `streamlit_app.py`

Local demo frontend.

It sends chat messages to the FastAPI backend. The assignment deployment should use the FastAPI backend URL, not the Streamlit URL.

## API Specification

The API is stateless. Every `POST /chat` request must include the full conversation history.

### `GET /health`

Request:

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### `POST /chat`

Request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a Java developer who works with stakeholders"
    },
    {
      "role": "assistant",
      "content": "What seniority level or years of experience are you hiring for?"
    },
    {
      "role": "user",
      "content": "Mid-level, around 4 years"
    }
  ]
}
```

Response:

```json
{
  "reply": "Here are 5 SHL assessments that match your requirements.",
  "recommendations": [
    {
      "name": "Java 8 (New)",
      "url": "https://www.shl.com/...",
      "test_type": "K"
    }
  ],
  "end_of_conversation": false
}
```

## Response Rules

- `reply` always contains the assistant message.
- `recommendations` is empty during clarification or refusal.
- `recommendations` contains structured SHL assessment records when recommending.
- `end_of_conversation` is always included because the assignment schema requires it.
- Recommendation URLs must come from the cached SHL catalog.

## How The System Works

1. FastAPI starts from `app.py`.
2. The shared recommender is initialized.
3. The cached SHL catalog is loaded from `data/catalog_cache.json`.
4. Catalog records are converted into LangChain documents.
5. FAISS builds an in-memory vector store using HuggingFace embeddings.
6. The frontend or evaluator sends a stateless message history to `/chat`.
7. The backend rebuilds conversation memory from the messages.
8. Guardrails check prompt-injection patterns.
9. The routing service decides whether to clarify, recommend, compare, or refuse.
10. If recommendation is needed, FAISS retrieves the most relevant catalog records.
11. The API returns the required schema.

## Conversation Behavior

### Clarify

For vague input, the assistant asks a question instead of recommending immediately.

Example:

```text
I need an assessment.
```

Possible response:

```text
What type of role are you hiring for?
```

### Recommend

Once enough context is available, the assistant returns a shortlist.

Useful context includes:

- Role
- Seniority or years of experience
- Skill focus such as technical, personality, cognitive, leadership, or communication

### Refine

If the user changes constraints, the full message history is used as the new retrieval query.

Example:

```text
Actually, add personality assessments too.
```

### Compare

Comparison-style requests are routed separately.

Example:

```text
What is the difference between OPQ and GSA?
```

### Refuse

The assistant refuses requests outside SHL assessment selection.

Examples:

- General hiring advice
- Legal questions
- Salary questions
- Immigration or visa questions
- Weather, politics, sports, recipes, or unrelated topics
- Prompt-injection attempts

## Guardrails

Prompt-injection checks run before the LLM call.

Blocked patterns include:

- `ignore previous instructions`
- `ignore the system prompt`
- `show me the system prompt`
- `developer message`
- `reveal your prompt`
- `jailbreak`
- `bypass your rules`

## Local Setup

Python 3.11 or 3.12 is recommended.

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create `.env`

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
API_URL=http://127.0.0.1:8000
```

Environment variables:

- `GROQ_API_KEY` is required.
- `GROQ_MODEL` controls the Groq model.
- `EMBEDDING_MODEL` controls the HuggingFace embedding model.
- `API_URL` is used only by the Streamlit frontend.

## Run Locally

### Backend

```powershell
uvicorn app:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

FastAPI docs:

```text
http://127.0.0.1:8000/docs
```

### Frontend

Start the backend first, then run:

```powershell
streamlit run streamlit_app.py
```

## Railway Deployment

This project is intended to deploy the FastAPI backend on Railway.

The deployed Railway URL is the URL to submit for the assignment because the evaluator needs access to:

- `/health`
- `/chat`

### Railway start command

Use this Railway start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### Railway environment variables

Add these variables in Railway:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

`API_URL` is not required for the Railway backend unless you are also running the Streamlit frontend separately.

### Railway deployment steps

1. Push this project to GitHub.
2. Create a new Railway project.
3. Choose Deploy from GitHub repo.
4. Select the repository containing this `SHL Assignment` project.
5. Set the Railway start command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

6. Add the required environment variables in Railway.
7. Deploy the service.
8. Open the Railway public domain.
9. Test the health endpoint:

```text
https://your-railway-domain.up.railway.app/health
```

Expected response:

```json
{"status":"ok"}
```

10. Use the Railway backend URL as the assignment submission API endpoint.

## Railway API Test

After deployment, test `/chat` with:

```bash
curl -X POST https://your-railway-domain.up.railway.app/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "I am hiring a mid-level Java developer who works with stakeholders and needs technical assessment."
      }
    ]
  }'
```

## Local Verification Commands

Compile the backend files:

```powershell
python -m compileall app.py api services rag scraper utils
```

Check that the FastAPI app imports:

```powershell
python -c "import app; print(app.app.title)"
```

Check catalog size:

```powershell
python -c "from scraper.catalog_loader import load_catalog; print(len(load_catalog()))"
```

Check registered routes:

```powershell
python -c "import app; print([route.path for route in app.app.routes])"
```

## Evaluation Alignment

The assignment evaluator checks:

- API schema compliance.
- `GET /health` returns status `ok`.
- `POST /chat` returns `reply`, `recommendations`, and `end_of_conversation`.
- Recommendations come from the SHL catalog.
- Vague requests are clarified before recommendation.
- Off-topic and prompt-injection requests are refused.
- The conversation fits within the assignment turn and timeout limits.

This project supports those requirements by:

- Keeping all schemas in `api/models.py`.
- Keeping the API stateless.
- Loading recommendations from cached SHL catalog data.
- Using FAISS retrieval for assessment matching.
- Using routing logic before recommendation.
- Returning empty recommendations during clarification and refusal.

## Approach Summary

### Retrieval setup

The cached SHL catalog is loaded from JSON. Each assessment becomes a LangChain document with the assessment name, description, job levels, languages, assessment length, and URL.

FAISS indexes those documents with HuggingFace embeddings. During recommendation, the full conversation history is used as the retrieval query.

### Prompt design

The LLM is mainly used for routing. It decides whether the assistant should clarify, recommend, compare, or refuse.

The system asks for JSON output so the backend can make predictable decisions.

### Recommendation design

Recommendations are created from FAISS document metadata. This keeps names, URLs, and test types tied to the cached SHL catalog.

### Evaluation approach

Manual checks should include:

- Vague query should clarify.
- Specific role query should recommend.
- Off-topic query should refuse.
- Prompt-injection query should refuse.
- Refinement query should update retrieval based on the full history.
- `/health` should return `{"status":"ok"}`.

## Troubleshooting

### `GROQ_API_KEY missing in .env`

Add `GROQ_API_KEY` locally or in Railway environment variables.

### Railway build succeeds but app fails to start

Check that the Railway start command is exactly:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```

### First request is slow

The app loads the embedding model and builds the FAISS vector store at startup. This can make cold starts slower.

### Catalog file not found

Make sure this file exists in the deployed project:

```text
data/catalog_cache.json
```

The root `catalog_cache.json` file is also present as a fallback.

## Assignment Submission Checklist

Before submitting the Railway URL:

- Railway deployment is active.
- `https://your-railway-domain.up.railway.app/health` returns `{"status":"ok"}`.
- `https://your-railway-domain.up.railway.app/chat` accepts the required JSON body.
- `POST /chat` returns the required schema.
- `GROQ_API_KEY` is set in Railway.
- `data/catalog_cache.json` is included in the repository.
- The submitted URL is the Railway FastAPI backend URL.

## Final Run Commands

Local backend:

```powershell
uvicorn app:app --reload
```

Local frontend:

```powershell
streamlit run streamlit_app.py
```

Railway backend:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```
