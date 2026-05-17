from fastapi import APIRouter, HTTPException

from api.models import ChatRequest, ChatResponse
from services.recommender import SHLRecommender


"""
Purpose:
This file contains FastAPI endpoints only.

Workflow:
1. /health confirms the backend is running.
2. /chat accepts the conversation and asks the recommender service for a reply.

Why this exists:
Routes should stay focused on HTTP details. The recommendation logic lives in
services/, so debugging API errors and debugging RAG logic are separate jobs.
"""


# APIRouter keeps endpoint definitions separate from the FastAPI app object.
router = APIRouter()

# One shared recommender instance is reused for all requests.
recommender = SHLRecommender()


@router.get("/health")
async def health():
    # Simple endpoint used to check that the backend process is alive.
    return {
        "status": "ok",
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):
    # Keep the endpoint thin: validate input, call the service, return output.
    try:
        return recommender.chat(
            request.messages,
        )

    # Preserve FastAPI HTTP errors exactly as they were raised.
    except HTTPException:
        raise

    # Convert unexpected internal errors into the same 500 response shape.
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
