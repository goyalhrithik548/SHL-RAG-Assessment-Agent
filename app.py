from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import recommender, router


"""
Purpose:
This file is intentionally tiny. It creates the FastAPI app and connects the
API routes from api/routes.py.

Workflow:
1. FastAPI starts.
2. The shared recommender is initialized during startup.
3. Route definitions are loaded from api/routes.py.

Why this exists:
Keeping app.py small makes the backend entry point easy to understand and
keeps the business logic out of the web-server setup file.
"""


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load the SHL catalog and FAISS vector store before the first request.
    recommender.initialize()

    # FastAPI runs the app while this generator is active.
    yield


# This object is what uvicorn imports when you run: uvicorn app:app --reload
app = FastAPI(
    title="SHL Assessment Recommender",
    lifespan=lifespan,
)

# All endpoint definitions live in api/routes.py.
app.include_router(router)
