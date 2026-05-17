from typing import Literal

from pydantic import BaseModel, Field


"""
Purpose:
This file contains every Pydantic model used by the FastAPI API.

Workflow:
1. The frontend sends JSON to /chat.
2. FastAPI validates that JSON with ChatRequest and Message.
3. The backend returns JSON shaped by ChatResponse and Recommendation.

Why this exists:
Keeping request and response shapes in one file makes the API schema easier to
find and avoids hunting through business logic when debugging validation errors.
"""


class Message(BaseModel):
    # The UI only sends user and assistant messages.
    role: Literal["user", "assistant"]

    # The actual text from the chat history.
    content: str


class ChatRequest(BaseModel):
    # The backend stays stateless, so the frontend sends the full conversation.
    messages: list[Message]


class Recommendation(BaseModel):
    # Name shown in the Streamlit recommendation list.
    name: str

    # SHL catalog URL for the assessment.
    url: str

    # Original test type string from the catalog cache.
    test_type: str


class ChatResponse(BaseModel):
    # Main assistant message shown in the chat.
    reply: str

    # Empty unless the routing logic decides to recommend assessments.
    recommendations: list[Recommendation] = Field(default_factory=list)

    # Kept for API compatibility with the existing frontend.
    end_of_conversation: bool = False
