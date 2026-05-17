import os
import threading
import time

from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_groq import ChatGroq

from api.models import ChatResponse
from rag.vector_store import build_vector_store
from scraper.catalog_loader import load_catalog
from services.memory_service import build_memory
from services.recommendation_service import recommend
from services.routing_service import route_request
from utils.guardrails import contains_prompt_injection


"""
Purpose:
This file contains the main SHLRecommender class.

Workflow:
1. Load the catalog from disk.
2. Build the FAISS vector store.
3. Rebuild memory from the stateless chat messages.
4. Route the request as clarify, recommend, compare, or refuse.
5. Return either a text-only response or recommendations.

Why this exists:
This is the orchestration layer. It connects the smaller services without
putting HTTP code, FAISS setup code, or helper functions in one large file.
"""


# Load environment variables from .env before reading GROQ_MODEL or GROQ_API_KEY.
load_dotenv()


class SHLRecommender:
    """
    Beginner-friendly coordinator for the SHL RAG workflow.

    The class owns the catalog and vector store because those are expensive to
    load and should be reused across requests.
    """

    def __init__(self):
        # Raw catalog entries loaded from catalog_cache.json.
        self.catalog = []

        # FAISS vector store built from the catalog.
        self.vector_store = None

        # Embedding model can be overridden from .env.
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        )

        # Groq model can be overridden from .env.
        self.groq_model = os.getenv(
            "GROQ_MODEL",
            "llama-3.1-8b-instant",
        )

        # _ready prevents expensive initialization from running twice.
        self._ready = False

        # The lock protects initialization if two requests arrive together.
        self._lock = threading.Lock()

    def initialize(self):
        """
        Load the catalog and vector store once.

        This method is called during FastAPI startup and again defensively from
        chat(). Calling it multiple times is safe.
        """
        if self._ready:
            return

        with self._lock:
            if self._ready:
                return

            start_time = time.time()

            # Catalog loading lives in scraper/catalog_loader.py.
            self.catalog = load_catalog()

            # FAISS building lives in rag/vector_store.py.
            self.vector_store = build_vector_store(
                self.catalog,
                self.embedding_model_name,
            )

            self._ready = True

            elapsed = round(time.time() - start_time, 2)

            print(
                f"Loaded {len(self.catalog)} assessments in {elapsed}s",
            )

    def _get_llm(self):
        """
        Create the Groq chat model used by the router.

        This keeps the original behavior: if GROQ_API_KEY is missing, the
        request fails instead of silently falling back.
        """
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY missing in .env",
            )

        return ChatGroq(
            model=self.groq_model,
            temperature=0,
            groq_api_key=api_key,
        )

    def chat(self, messages):
        """
        Main public method used by the /chat endpoint.

        The frontend sends the full conversation each time, so this method
        rebuilds memory from the request instead of storing server-side state.
        """
        self.initialize()

        if not messages:
            raise HTTPException(
                status_code=400,
                detail="messages cannot be empty",
            )

        # Match the previous app.py behavior by reading the final message.
        last_user_message = messages[-1].content.strip()

        # Guardrails run before sending anything to the LLM.
        if contains_prompt_injection(last_user_message):
            return ChatResponse(
                reply="I can only help with SHL assessments.",
                recommendations=[],
                end_of_conversation=False,
            )

        # Rebuild stateless memory from the whole message list.
        history_text = build_memory(messages)

        # Ask the routing service what kind of response is needed.
        route = route_request(
            history_text=history_text,
            last_user_message=last_user_message,
            get_llm=self._get_llm,
        )

        action = route.get("action", "recommend")
        reply = route.get("reply", "")

        # Refusal and clarification return text only, just like the original.
        if action == "refuse":
            return ChatResponse(
                reply=reply,
                recommendations=[],
                end_of_conversation=False,
            )

        if action == "clarify":
            return ChatResponse(
                reply=reply,
                recommendations=[],
                end_of_conversation=False,
            )

        # The old app allowed compare to fall through into recommendation.
        # Keeping that behavior preserves the existing compare flow.
        return recommend(
            vector_store=self.vector_store,
            history_text=history_text,
        )
