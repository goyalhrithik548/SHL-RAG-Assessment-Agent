from pathlib import Path


"""
Purpose:
This file stores shared constants used across the backend.

Workflow:
Services import these values instead of repeating URLs, labels, cache paths, or
keyword lists in multiple files.

Why this exists:
Constants are easier to update and debug when they live in one predictable
place.
"""


# Root folder of the project.
BASE_DIR = Path(__file__).resolve().parents[1]

# Data folder requested in the refactored project structure.
DATA_DIR = BASE_DIR / "data"

# Preferred cache location after refactor.
CACHE_PATH = DATA_DIR / "catalog_cache.json"

# Older cache location from the working project.
ROOT_CACHE_PATH = BASE_DIR / "catalog_cache.json"

# Try the new location first, then the old one for compatibility.
CATALOG_CACHE_CANDIDATES = [
    CACHE_PATH,
    ROOT_CACHE_PATH,
]

# SHL catalog URLs kept from the original app.py.
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
DIRECT_CATALOG_URL = "https://www.shl.com/products/product-catalog/"

# Headers kept for any future scraper/catalog refresh logic.
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

# Test type labels kept from the original app.py.
TEST_TYPE_LABELS = {
    "A": "Ability and Aptitude",
    "B": "Biodata and Situational Judgement",
    "C": "Competency Based",
    "D": "Development and 360",
    "E": "Assessment Exercises",
    "K": "Knowledge and Skills",
    "P": "Personality and Behaviour",
    "S": "Simulations",
}

# Prompt-injection phrases blocked before calling the LLM.
INJECTION_PATTERNS = [
    "ignore previous instructions",
    "ignore the system prompt",
    "show me the system prompt",
    "developer message",
    "reveal your prompt",
    "jailbreak",
    "bypass your rules",
]

# Off-topic words used by fallback routing.
OFF_TOPIC_WORDS = [
    "salary",
    "visa",
    "immigration",
    "movie",
    "sports",
    "recipe",
    "weather",
    "politics",
]

# Role words used by fallback clarification logic.
ROLE_KEYWORDS = [
    "developer",
    "engineer",
    "manager",
    "analyst",
    "sales",
    "java",
    "python",
    "intern",
]

# Seniority words used by fallback clarification logic.
SENIORITY_KEYWORDS = [
    "junior",
    "mid",
    "senior",
    "lead",
    "manager",
    "experience",
    "years",
    "4 years",
    "5 years",
]

# Skill/focus words used by fallback clarification logic.
SKILL_FOCUS_KEYWORDS = [
    "stakeholder",
    "communication",
    "technical",
    "personality",
    "leadership",
    "coding",
    "aptitude",
    "behavior",
    "cognitive",
]
