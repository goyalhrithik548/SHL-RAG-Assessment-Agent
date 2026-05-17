import json

from utils.constants import CATALOG_CACHE_CANDIDATES


"""
Purpose:
This file loads the cached SHL catalog from disk.

Workflow:
1. Look for data/catalog_cache.json first, matching the refactored structure.
2. Fall back to catalog_cache.json at the project root for backward compatibility.
3. Return the catalog as a Python list of dictionaries.

Why this exists:
Catalog loading is separate from recommendation logic, so file-path issues are
easy to find and fix.
"""


def load_catalog():
    """
    Load the cached SHL catalog.

    The project is expected to use data/catalog_cache.json after this refactor,
    but the root-level fallback avoids breaking an older working copy.
    """
    for cache_path in CATALOG_CACHE_CANDIDATES:
        if cache_path.exists():
            return json.loads(
                cache_path.read_text(encoding="utf-8"),
            )

    raise RuntimeError(
        "catalog_cache.json not found",
    )
