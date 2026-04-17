# """
#  Request Validation & Pydantic Integration
# =================================================
# WHAT YOU'LL LEARN:
# - Separate Pydantic models for Create/Update/Response (industry pattern)
# - Field validation (min/max values, string lengths)
# - Partial updates with PATCH
# - Proper HTTP status codes (this is what interviewers test!)
 
# WHY SEPARATE MODELS?
# Imagine a User:
# - When CREATING: you send {name, email, password}     → UserCreate
# - When UPDATING: you send {name} or {email} (partial) → UserUpdate  
# - When RESPONDING: you send {id, name, email, created} → UserResponse (NO password!)
 
# Different situations need different shapes of the same data.
# This is called the "DTO pattern" (Data Transfer Object).
 
# HOW TO RUN:
#     uvicorn day9_validation:app --reload
#     Open: http://localhost:8000/docs
# """

# from fastapi import FastAPI, HTTPException, Query, Path
# from pydantic import BaseModel, Field
# from datetime import datetime


# app = FastAPI(
#     title='Book API v2 - with Validation',
#     description="With proper pydantic models and validation",
#     version="2.0"
# )


# # =============================================================================
# # STEP 1: Pydantic Models — The Right Way
# # =============================================================================
# # In Day 8, we used one simple model. In real apps, you need MULTIPLE models
# # for the same resource. Here's the industry-standard pattern:
 


# class BookCreate(BaseModel):

#     """
#     What the client sends when CREATING a book.
    
#     Field() lets you add validation rules:
#     - min_length/max_length for strings
#     - ge (greater or equal) / le (less or equal) for numbers
#     - description shows up in the /docs page!
    
#     INTERVIEW TIP: "Pydantic Field validators run automatically. If a client 
#     sends a rating of 6.0, FastAPI returns 422 with a clear error message 
#     before your code even runs."
#     """
#     title:str = Field(
#         ...,
#         min_length=1,
#         max_length=200,
#         description="The book's title",
#         examples=["The Pragramatic Programmer"]
#     )

#     author:str = Field(
#         ...,
#         min_length=1, 
#         max_length=100,
#         description="The author's name",
#     )

#     genre:str = Field(
#         ..., 
#         min_length=1, 
#         max_length=50,
#         description="Book genre (e.g., 'programming', 'sci-fi', 'fantasy')",
#     )

#     year:int = Field(
#         ..., 
#         ge=1000,                    # ge = greater than or equal
#         le=2026,                    # le = less than or equal
#         description="Year published (1000-2026)",
#     )

#     rating:int = Field(
#         default=0.0,
#         ge=0.0,
#         le=5.0,
#         description="Rating of the book",
#     )

# class BookUpdate(BaseModel):
#     """
#     What the client sends when UPDATING a book (PATCH).
    
#     KEY DIFFERENCE: ALL fields are Optional!
#     The client only sends what they want to change.
    
#     Example — to change only the rating:
#     PATCH /books/1  body: {"rating": 4.9}
    
#     The other fields (title, author, etc.) stay the same.
#     This is called a "partial update."
#     """
#     title: str | None = Field(default=None, min_length=1, max_length=200)
#     author: str | None = Field(default=None, min_length=1, max_length=100)
#     genre: str | None = Field(default=None, min_length=1, max_length=50)
#     year: int | None = Field(default=None, ge=1000, le=2026)
#     rating: float | None = Field(default=None, ge=0.0, le=5.0)

# class BookResposne(BaseModel):
#     """
#     What the API sends BACK to the client.
    
#     This includes fields the client never sends (id, created_at, updated_at).
#     These are server-generated.
    
#     WHY A SEPARATE RESPONSE MODEL?
#     - You might have internal fields you DON'T want to expose
#     - You control exactly what the client sees
#     - In a User API, you'd NEVER include password_hash in the response!
#     """
#     id:int
#     title:str
#     author: str
#     genre: str
#     year: int
#     rating: float
#     created_at: str
#     updated_at: str


# class BookListResponse(BaseModel):
#     count:int
#     books:list[BookResposne]


# # =============================================================================
# # STEP 2: Better in-memory storage (simulates a real database)
# # =============================================================================
 
# def _now() -> str:
#     """Current timestamp as ISO string."""
#     return datetime.now().isoformat()

# # Our "database" - now with timestamps!

# books_db:dict[int, dict] = {}
# next_id = 1

# def _seedbooks():
#     """Add some starter books. Called when the app starts."""
#     global next_id

#     starter_books=[{"title": "The Pragmatic Programmer", "author": "David Thomas", "genre": "programming", "year": 2019, "rating": 4.7},
#         {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "genre": "programming", "year": 2017, "rating": 4.8},
#         {"title": "Dune", "author": "Frank Herbert", "genre": "sci-fi", "year": 1965, "rating": 4.6
#         }]
    
#     for book_data in starter_books:
#         now = _now()
#         books_db[next_id] = {
#             "id": next_id,
#             **book_data,
#             "created_at": now,
#             "updated_at": now,
#         }
#         next_id += 1


# _seedbooks()

# # =============================================================================
# # STEP 3: Endpoints with proper validation & status codes
# # =============================================================================
# """
# HTTP STATUS CODES — Know these for interviews!
 
# 2xx = SUCCESS:
#   200 OK              → Default for GET. "Here's your data."
#   201 Created          → For POST. "New resource was created."
#   204 No Content       → For DELETE. "Done, nothing to return."
 
# 4xx = CLIENT ERROR (the caller messed up):
#   400 Bad Request      → Generic "your request is wrong"
#   401 Unauthorized     → "You need to log in" (no token)
#   403 Forbidden        → "You're logged in but not allowed"
#   404 Not Found        → "This resource doesn't exist"
#   422 Unprocessable    → "Your data failed validation" (FastAPI's default)
 
# 5xx = SERVER ERROR (our code messed up):
#   500 Internal Server  → "Something crashed on our end"
#   503 Service Unavail  → "Server is down for maintenance"
# """


# @app.get("/books", response_model=BookResposne)
# def list_books(
#     genre: str | None = Query(
#         default=None,
#         description="Filter by genre (case-insensitive)",
#         examples=["programming", "sci-fi"],
#     ),
#     min_rating:float | None = Query(
#         default=None,
#         ge=0.0,
#         le=5.0,
#         description="Minimum rating filter",
#     ),
#     limit: int = Query(
#         default=10,
#         ge=1,
#         le=100,
#         description="Max number of results",
#     ),
# ):

#     """
#     List all books with optional filters.
    
#     NEW CONCEPTS:
    
#     1. response_model=BookListResponse
#        → FastAPI will validate OUR response too!
#        → If we accidentally include extra fields, they get stripped
#        → The /docs page shows exactly what the client will receive
    
#     2. Query() with validation
#        → Just like Field() for models, but for query parameters
#        → ge, le, description, examples all work the same way
    
#     Try: /books?genre=programming&min_rating=4.5&limit=5
#     """

#     results = list(books_db.values())

#     if genre:
#         results = [b for b in results if b["genre"].lower() == genre.lower()]
    
#     if min_rating is not None:
#         results = [b for b in results if b["rating"] >= min_rating]
    
#     results = results[:limit]
    
#     return {"count": len(results), "books": results}


# @app.get("/books/{book_id}", response_model=BookResponse)
# def get_book(
#     book_id: int = Path(
#         ...,
#         ge=1,                       # Book IDs start at 1
#         description="The ID of the book to retrieve",
#     ),
# ):
#     """
#     Get a single book by ID.
    
#     Path() is like Query() but for path parameters.
#     ge=1 means "must be >= 1", so /books/0 or /books/-1 → 422 error.
#     """
#     if book_id not in books_db:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Book with id {book_id} not found.",
#         )
#     return books_db[book_id]
 
 
# @app.post("/books", response_model=BookResponse, status_code=201)
# def create_book(book: BookCreate):
#     """
#     Create a new book.
    
#     status_code=201: The proper code for "resource created."
    
#     WHAT HAPPENS AUTOMATICALLY:
#     1. Client sends JSON → FastAPI parses it
#     2. Pydantic validates ALL fields:
#        - title must be 1-200 chars
#        - year must be 1000-2026
#        - rating must be 0.0-5.0
#     3. If validation fails → 422 response with DETAILED errors
#     4. If valid → your code runs
#     5. Response is validated against BookResponse model
    
#     Try sending bad data in /docs and watch the error messages!
#     """
#     global next_id
    
#     now = _now()
#     new_book = {
#         "id": next_id,
#         **book.model_dump(),
#         "created_at": now,
#         "updated_at": now,
#     }
#     books_db[next_id] = new_book
#     next_id += 1
    
#     return new_book
 
 
# @app.patch("/books/{book_id}", response_model=BookResponse)
# def update_book(book_id: int, updates: BookUpdate):
#     """
#     Partially update a book.
    
#     PATCH vs PUT:
#     - PUT = "Replace the ENTIRE resource" (send ALL fields)
#     - PATCH = "Update ONLY the fields I'm sending" (partial)
    
#     Example: PATCH /books/1 with {"rating": 5.0}
#     → Only changes the rating, everything else stays the same
    
#     The magic: model_dump(exclude_unset=True)
#     - This only returns fields the client ACTUALLY sent
#     - If they sent {"rating": 5.0}, we get {"rating": 5.0}
#     - NOT {"title": None, "author": None, "rating": 5.0, ...}
    
#     WHY THIS MATTERS FOR AI:
#     When building an LLM chat API, you'll PATCH conversation settings:
#     PATCH /conversations/123 body: {"temperature": 0.7}
#     Same pattern!
#     """
#     if book_id not in books_db:
#         raise HTTPException(status_code=404, detail=f"Book {book_id} not found.")
    
#     # exclude_unset=True → only get fields the client actually sent
#     update_data = updates.model_dump(exclude_unset=True)
    
#     if not update_data:
#         raise HTTPException(
#             status_code=400, 
#             detail="No fields provided to update.",
#         )
    
#     # Apply updates to existing book
#     book = books_db[book_id]
#     for key, value in update_data.items():
#         book[key] = value
#     book["updated_at"] = _now()
    
#     return book
 
 
# @app.delete("/books/{book_id}")
# def delete_book(book_id: int):
#     """Delete a book. Returns the deleted book for confirmation."""
#     if book_id not in books_db:
#         raise HTTPException(status_code=404, detail=f"Book {book_id} not found.")
    
#     deleted = books_db.pop(book_id)
#     return {"message": f"Deleted '{deleted['title']}'", "deleted_book": deleted}
 
 
# # =============================================================================
# # BONUS: Stats endpoint (preview of Day 10's aggregation)
# # =============================================================================
 
# @app.get("/books/stats/")
# def book_stats():
#     """
#     Get statistics about all books.
#     Trailing slash to avoid conflict with /books/{book_id}.
#     """
#     if not books_db:
#         return {"count": 0, "avg_rating": 0, "genres": {}}
    
#     all_books = list(books_db.values())
#     ratings = [b["rating"] for b in all_books]
    
#     # Count books per genre
#     genre_counts: dict[str, int] = {}
#     for book in all_books:
#         genre = book["genre"]
#         genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
#     return {
#         "count": len(all_books),
#         "avg_rating": round(sum(ratings) / len(ratings), 2),
#         "rating_range": {"min": min(ratings), "max": max(ratings)},
#         "genres": genre_counts,
#     }
 
 
# # =============================================================================
# # INTERVIEW PREP
# # =============================================================================
# """
# Q1: How does FastAPI validate request data automatically?
# A1: FastAPI uses Pydantic models to validate request bodies. When a request 
#     comes in, FastAPI:
#     1. Parses the JSON body
#     2. Creates a Pydantic model instance (this triggers validation)
#     3. If validation fails, returns 422 with detailed error messages
#     4. If valid, passes the model to your function
    
#     For query/path params, FastAPI uses Python type hints + Query()/Path() 
#     validators to do the same thing.
 
# Q2: What is the difference between 200, 201, 400, 404, and 422?
# A2: 
#     200 OK = Success, here's your data (default for GET/PATCH/PUT)
#     201 Created = Success, new resource created (for POST)
#     400 Bad Request = Your request is malformed or invalid
#     404 Not Found = The resource you asked for doesn't exist
#     422 Unprocessable Entity = Data format is correct but values are invalid
    
#     422 is FastAPI's default for validation errors. Example: 
#     You sent {"year": 9999} — it's valid JSON, valid int, but fails our 
#     le=2026 constraint.
 
# Q3: How would you version your API?
# A3: Common approaches:
#     - URL versioning: /api/v1/books, /api/v2/books (most common, easiest)
#     - Header versioning: Accept: application/vnd.myapi.v2+json
#     - Query param: /books?version=2
    
#     In FastAPI, URL versioning with APIRouter:
    
#     from fastapi import APIRouter
#     v1 = APIRouter(prefix="/api/v1")
#     v2 = APIRouter(prefix="/api/v2")
    
#     @v1.get("/books") 
#     def list_books_v1(): ...
    
#     @v2.get("/books")  
#     def list_books_v2(): ...   # New response format
    
#     app.include_router(v1)
#     app.include_router(v2)
 
# HOW TO TEST:
#     uvicorn day9_validation:app --reload
    
#     Test validation by sending BAD data in /docs:
#     1. POST /books with {"title": "", ...}     → 422 (title too short)
#     2. POST /books with {"year": 9999, ...}    → 422 (year > 2026)
#     3. POST /books with {"rating": 6.0, ...}   → 422 (rating > 5.0)
#     4. PATCH /books/1 with {}                   → 400 (no fields to update)
#     5. GET /books/0                             → 422 (id must be >= 1)
#     6. GET /books/999                           → 404 (book doesn't exist)
 
# GIT COMMIT: Day 9: validated book API with Pydantic models + proper status codes
# """
 

# import asyncio

# class FoodTruck:
#     async def __aenter__(self):          # Async setup
#         print("🚛 Driving to location...")
#         await asyncio.sleep(2)
#         print("🚛 Setting up kitchen...")
#         await asyncio.sleep(1)
#         print("🚛 OPEN for business!")
#         return self                       # "self" is what you get after "as"

#     async def __aexit__(self, *args):    # Async cleanup
#         print("🚛 Packing up...")
#         await asyncio.sleep(1)
#         print("🚛 Closed for the day!")

#     async def serve(self, dish):
#         print(f"   🍔 Serving {dish}...")
#         await asyncio.sleep(0.5)
#     async def serve1(self, dish):
#         await asyncio.sleep(3)
#         print(f"   🍔 Serving {dish}...")
# async def main():
#     async with FoodTruck() as truck:     # Awaits setup
#         task1 = asyncio.create_task(truck.serve("burger"));
#         task2 = asyncio.create_task(truck.serve1("fries"));

#         print("Task1")
#         print("Task2")
#         task3 = asyncio.create_task(truck.serve("sandwich"));

#         await task1
#         await task2
#         await task3
#     # Awaits cleanup automatically, even if an error happened

# asyncio.run(main())


#ASYNC CHALLENGE 1 - The Coutndown
import asyncio
import time
import random

# async def countdown(name: str, n: int):
#     if n==0:
#         await asyncio.sleep(1)
#         print(f'{name} - {n}')
#         return
#     await asyncio.sleep(1)
#     print(f'{name} - {n}')
#     await countdown(name, n-1)

# async def main():
#     task1 = asyncio.create_task(countdown("VK", 5))
#     task2 = asyncio.create_task(countdown("AB", 3))

#     await task1
#     await task2

# asyncio.run(main())

#Challenge 2 — "The Slow API"
# async def fetch_user():
#     print("Calling fetch user API")
#     await asyncio.sleep(2)
#     print("fech user call is completed")

# async def fetch_comments():
#     print("Calling fetch comments API")
#     await asyncio.sleep(1)
#     print("fech comments call is completed")

# async def fetch_posts():
#     print("Calling fetch posts API")
#     await asyncio.sleep(3)
#     print("fech posts call is completed")

# async def main():
#     start = time.perf_counter()

#     await asyncio.gather(
#         fetch_comments(),
#         fetch_posts(),
#         fetch_user() 
#     )

#     elapsed = time.perf_counter() - start
#     print(elapsed)

# asyncio.run(main())


# CHALLENGE 3 First One Wins

async def server(name):
    delay = random.uniform(1,5)
    print(f"  {name}: processing... (will take {delay:.1f}s)")
    await asyncio.sleep(delay)
    return f"{name} responded!"


async def main():

    task1 = asyncio.create_task(server("Server A"))
    task2 = asyncio.create_task(server("Server B"))
    task3 = asyncio.create_task(server("Server C"))


    done, pending = await asyncio.wait([task1, task2, task3], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()
    
    print(done.pop().result())

asyncio.run(main())