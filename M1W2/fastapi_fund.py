"""
DAY 8: FastAPI Fundamentals — Routes, Params, Docs
====================================================
⏱ 1.5 hrs | Difficulty: Beginner-friendly
 
WHAT IS FastAPI?
Think of it like this:
- Your Python code is like a chef in a kitchen
- FastAPI is the RESTAURANT that lets customers (other apps, browsers, phones)
  send orders (requests) to your chef and get food (responses) back
- Without FastAPI, your code just sits there. With it, anyone on the internet
  can talk to your code!
 
WHY FastAPI (not Flask/Django)?
1. It's FAST (hence the name) — async by default
2. It validates data automatically (using Pydantic — you already learned this!)
3. It creates beautiful API docs FOR FREE at /docs
4. Every AI company uses it — it's THE framework for AI apps
 
HOW TO RUN THIS:
    pip install fastapi uvicorn
    uvicorn day8_fastapi_fundamentals:app --reload
 
    Then open: http://localhost:8000/docs  ← THIS IS MAGIC, explore it!
 
WHAT IS UVICORN?
- Uvicorn is the "waiter" that takes HTTP requests from the internet
  and hands them to your FastAPI app
- --reload means "restart automatically when I change the code" (dev only!)
 
WHAT IS ASGI vs WSGI?
- WSGI (old): handles ONE request at a time, like a single cashier
- ASGI (new): handles MANY requests at once, like multiple cashiers
- FastAPI uses ASGI = perfect for AI apps that make slow API calls to LLMs
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# =============================================================================
# STEP 1: Create the app
# =============================================================================
# This ONE line creates your entire web application.
# Think of it as opening your restaurant for business.


app = FastAPI(
    title="My Book API",
    description="My first FastAPI app - a Book API!",
    version="1.0.0"
)

# =============================================================================
# STEP 2: In-memory "database" (just a Python dictionary for now)
# =============================================================================
# We'll replace this with a REAL database on Day 10.
# For now, a dict is perfect for learning how APIs work.
 
# We use an integer ID as the key, and a dict of book info as the value.
# Think of it like a filing cabinet where each drawer number (ID) has a folder (book).


books_db:dict[int, dict] = {
    1: {
        "id": 1,
        "title": "The Pragmatic Programmer",
        "author": "David Thomas & Andrew Hunt",
        "genre": "programming",
        "year": 2019,
        "rating": 4.7,
    },
    2: {
        "id": 2,
        "title": "Designing Data-Intensive Applications",
        "author": "Martin Kleppmann",
        "genre": "programming",
        "year": 2017,
        "rating": 4.8,
    },
    3: {
        "id": 3,
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "sci-fi",
        "year": 1965,
        "rating": 4.6,
    },
}

# Auto-incrementing ID counter (simulates what a database does automatically)
next_id:int = 4


# =============================================================================
# STEP 3: Pydantic model for creating a book
# =============================================================================
# Remember Pydantic from Day 3? FastAPI uses it to:
# 1. Validate incoming data (reject bad requests automatically!)
# 2. Generate the request body schema in /docs
# 3. Convert JSON → Python objects automatically
#
# This model says: "To create a book, you MUST send title, author, genre, year.
# Rating is optional and defaults to 0.0"


class Book(BaseModel):
    title:str
    authot:str
    genre:str
    year:int
    rating:float = 0.0


# =============================================================================
# STEP 4: Define your API endpoints (routes)
# =============================================================================
# An "endpoint" = a URL path + an HTTP method.
#
# HTTP Methods (think of them as VERBS — what action do you want?):
#   GET    = "Give me data"         (reading)
#   POST   = "Here's new data"      (creating)
#   PUT    = "Replace this data"     (full update)
#   PATCH  = "Change part of this"   (partial update)
#   DELETE = "Remove this data"      (deleting)
#
# The combination of METHOD + PATH = an endpoint:
#   GET  /books       → list all books
#   GET  /books/1     → get book with id 1
#   POST /books       → create a new book
#   DELETE /books/1   → delete book with id 1
 
# --- ROOT ENDPOINT ---
# The simplest possible endpoint. Visit http://localhost:8000/ to see it.

@app.get("/")
def read_root():
    """
    Welcome endpoint. Just returns a greeting.
    
    The @app.get("/") decorator says:
    "When someone sends a GET request to /, run this function"
    """
    return {"message": "Welcome to the Book API! Visit /docs for interactive docs."}

# --- GET ALL BOOKS (with optional filtering) ---

@app.get("/books")
def list_books(genre:str | None = None):
  """
    List all books, optionally filtered by genre.
    
    QUERY PARAMETERS explained:
    - These are the ?key=value parts in a URL
    - Example: /books?genre=sci-fi
    - They're used for OPTIONAL filtering/sorting/pagination
    - FastAPI detects them automatically from function parameters!
    
    The 'genre' parameter:
    - str | None = None means "this is optional, defaults to None"
    - If someone visits /books → genre is None → return ALL books
    - If someone visits /books?genre=sci-fi → genre is "sci-fi" → return only sci-fi
    
    WHY THIS MATTERS FOR AI:
    When you build a RAG API, you'll have endpoints like:
    GET /search?query=how+to+train+a+model&limit=10&threshold=0.7
    Same concept — query params for filtering!
    """

  all_books = list(books_db.values())
  if genre:
     all_books = [book for book in all_books if b["genere"].lower() == genre.lower()]
  
  return {"count": len(all_books), "books": all_books}


@app.get("/books/{book_id}")
def get_book(book_id:int):
  """
    Get a single book by its ID.
    
    PATH PARAMETERS explained:
    - These are part of the URL itself: /books/1, /books/2, /books/42
    - The {book_id} in the decorator becomes the function parameter
    - FastAPI automatically converts "1" (string from URL) → 1 (Python int)!
    - If someone sends /books/abc, FastAPI returns a 422 error automatically
    
    PATH PARAMS vs QUERY PARAMS:
    - Path params → identify a SPECIFIC resource: /books/1 (THE book with id 1)
    - Query params → FILTER or MODIFY the request: /books?genre=sci-fi
    
    Think of it like:
    - Path param = "I want THIS specific thing" (like an address)
    - Query param = "Show me things with these conditions" (like a search filter)
    
    HTTPException:
    - This is how you send error responses in FastAPI
    - status_code=404 means "Not Found" — the resource doesn't exist
    - The detail message tells the client what went wrong
    """
  if book_id not in books_db:
    raise HTTPException(
        status_code=404,
        detail=f"Book with id {book_id} not found. Try /books to see all books."
    )
  return books_db[book_id]

@app.post("/books", status_code=201)
def create_book(book: Book):
  """
    Create a new book.
    
    REQUEST BODY explained:
    - Unlike path/query params, the request body carries COMPLEX data
    - The client sends JSON in the body of the HTTP request
    - FastAPI + Pydantic automatically:
      1. Parse the JSON
      2. Validate all fields (correct types? required fields present?)
      3. Convert it to a Python BookCreate object
      4. Return 422 with details if validation fails
    
    Example JSON body:
    {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "genre": "programming",
        "year": 2008,
        "rating": 4.3
    }
    
    status_code=201:
    - 200 = "OK, here's your data" (default for GET)
    - 201 = "Created! A new resource was made" (proper for POST)
    - Using the right status codes is professional and expected in interviews!
    
    WHY THIS MATTERS FOR AI:
    When you build an LLM API, users will POST their prompts:
    POST /chat  with body: {"message": "explain quantum computing", "model": "gpt-4"}
    Same pattern — validating input with Pydantic!
    """
   
  global next_id

  new_book = book.model_dump()
  new_book["id"] = next_id;

  books_db[next_id] = new_book
  next_id += 1

  return new_book


# --- DELETE A BOOK ---
@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    """
    Delete a book by ID.
    
    DELETE is straightforward:
    - Check if the book exists → 404 if not
    - Remove it from storage
    - Return confirmation
    
    In a real app, you might "soft delete" (mark as deleted but keep the data)
    instead of actually removing it. We'll cover that concept with databases.
    """
    if book_id not in books_db:
        raise HTTPException(
            status_code=404,
            detail=f"Book with id {book_id} not found."
        )
    
    deleted_book = books_db.pop(book_id)  # .pop() removes AND returns the item
    return {"message": f"Deleted '{deleted_book['title']}'", "book": deleted_book}


@app.get("/books/search/")
def search_books(q: str, limit: int = 5):
    """
    Search books by title or author.
    
    Multiple query params:
    - /books/search/?q=pragmatic&limit=2
    - 'q' is REQUIRED (no default value) — FastAPI enforces this
    - 'limit' is OPTIONAL (defaults to 5)
    
    NOTE: This endpoint path has a trailing slash to avoid conflict
    with /books/{book_id}. In production, you'd structure routes more carefully.
    """
    q_lower = q.lower()
    results = [
        book for book in books_db.values()
        if q_lower in book["title"].lower() or q_lower in book["author"].lower()
    ]
    return {"query": q, "count": len(results[:limit]), "results": results[:limit]}
