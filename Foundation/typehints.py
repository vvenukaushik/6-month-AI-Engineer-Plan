'''Type hints tell Python (and other developers) what types your functions
expect and return. Python doesn't enforce them at runtime — but tools
like mypy catch type errors BEFORE your code runs.
 
WHY THIS MATTERS FOR AI ENGINEERING:
  - Every LLM SDK (OpenAI, Anthropic) is fully type-hinted
  - Pydantic (Day 3 Exercise 2) is BUILT on type hints
  - FastAPI uses type hints for automatic request validation
  - Instructor library uses them to get structured LLM outputs
  - Reading AI library source code requires understanding type hints
 
HOW TO RUN:
    python day3_type_hints.py
 
HOW TO TYPE-CHECK:
    pip install mypy
    mypy day3_type_hints.py'''

from typing import (
    Optional,       # Value can be X or None
    Union,          # Value can be X or Y
    Any,            # Any type (escape hatch — avoid when possible)
    Literal,        # Value must be one of specific strings/numbers
    TypedDict,      # Dict with specific key-value types
)

from datetime import datetime

# ══════════════════════════════════════════════════════════════
# BASIC TYPE HINTS
# ══════════════════════════════════════════════════════════════
 
# ── Simple types ───────────────────────────────────────────
# Since Python 3.10+ you can use built-in types directly (no imports needed)

def greet(name: str) -> str:
    """Parameter 'name' must be str, function returns str."""
    return f"Hello, {name}!"

def calculate_cost(price: float, quantity: int, tax_rate: float = 0.08) -> float:
    #Multiple parameters with a default value.
    return round(price*quantity*(1+tax_rate), 2)

# ── Collection types ──────────────────────────────────────
# Python 3.10+: use list[str], dict[str, int], tuple[int, ...] directly
 
def get_unique_words(text: str) -> list[str]:
    """Returns a list of strings."""
    return list(set(text.lower().split()))
 
 
def count_words(text: str) -> dict[str, int]:
    """Returns a dict mapping strings to integers."""
    counts: dict[str, int] = {}
    for word in text.lower().split():
        counts[word] = counts.get(word, 0) + 1
    return counts