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

def find_user(user_id: int) -> Optional[dict[str, str]]:
    """
    Optional[X] means "X or None".
    It's equivalent to: Union[X, None] or X | None
    
    Use Optional when a function might not find/return a result.
    This is EXTREMELY common in AI apps:
      - Vector search might return no matches
      - LLM parsing might fail to extract a field
      - Database lookup might find nothing
    """
    users = {
        1: {"name": "Alice", "role": "engineer"},
        2: {"name": "Bob", "role": "designer"},
    }
    return users.get(user_id)  # Returns None if not found
 
def parse_input(value: str | int | float) -> str:
    """
    Union types: str | int | float (Python 3.10+ syntax)
    Older syntax: Union[str, int, float]
    
    Use when a parameter genuinely accepts multiple types.
    """
    return str(value).strip()

def set_log_level(level: Literal["DEBUG", "INFO", "WARNING", "ERROR"]) -> str:
    """
    Literal restricts the value to specific options.
    mypy will flag any call with a value not in the list.
    
    AI usage: Literal["gpt-4o", "gpt-4o-mini", "claude-sonnet"] for model names.
    """
    return f"Log level set to {level}"


class APIResponse(TypedDict):
    """
    TypedDict defines a dictionary with specific keys and value types.
    
    Unlike a regular dict, mypy knows exactly what keys exist
    and what type each value should be.
    
    This is how you type API responses before graduating to Pydantic.
    """
    status: int
    message: str
    data: Optional[dict[str, Any]]


def make_api_response(status: int, message: str, data: Optional[dict[str, Any]] = None) -> APIResponse:
    """Returns a properly typed API response."""
    return APIResponse(status=status, message=message, data=data)


# ══════════════════════════════════════════════════════════════
# GENERICS — Type variables for flexible functions
# ══════════════════════════════════════════════════════════════
 
from typing import TypeVar
 
T = TypeVar("T")
 
def first_or_default(items: list[T], default: T) -> T:
    """
    TypeVar makes the function work with ANY type while keeping
    the relationship: if you pass list[int], you get int back.
    
    Without TypeVar, you'd have to use Any, which loses type info.
    
    >>> first_or_default([1, 2, 3], 0)      → int
    >>> first_or_default(["a", "b"], "x")    → str
    """
    return items[0] if items else default
 
 
def chunk_list(items: list[T], chunk_size: int) -> list[list[T]]:
    """
    Splits a list into chunks. Type is preserved.
    
    AI usage: chunking documents, batching embeddings, splitting data.
    This is a simplified version of what you'll build in Month 3 for RAG.
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
 
 
# ══════════════════════════════════════════════════════════════
# TYPE ALIASES — Making complex types readable
# ══════════════════════════════════════════════════════════════
 
# Without aliases: def process(data: list[dict[str, Union[str, int, list[str]]]]) → unreadable!
# With aliases: clean and self-documenting
 
Embedding = list[float]
DocumentChunk = dict[str, str | int | list[str]]
ConversationHistory = list[ChatMessage]
TokenCount = int
CostUSD = float
 
def compute_similarity(embedding_a: Embedding, embedding_b: Embedding) -> float:
    """
    Type aliases make the signature self-documenting.
    You immediately know this compares two embedding vectors.
    """
    # Cosine similarity (simplified — you'll learn the real version in Month 3)
    dot_product = sum(a * b for a, b in zip(embedding_a, embedding_b))
    magnitude_a = sum(a ** 2 for a in embedding_a) ** 0.5
    magnitude_b = sum(b ** 2 for b in embedding_b) ** 0.5
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)
 
 
def estimate_cost(
    input_tokens: TokenCount,
    output_tokens: TokenCount,
    cost_per_1k_input: CostUSD = 0.005,
    cost_per_1k_output: CostUSD = 0.015,
) -> CostUSD:
    """Type aliases make pricing logic clear."""
    input_cost = (input_tokens / 1000) * cost_per_1k_input
    output_cost = (output_tokens / 1000) * cost_per_1k_output
    return round(input_cost + output_cost, 6)
 