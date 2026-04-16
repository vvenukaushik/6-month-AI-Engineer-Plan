"""
DAY 10: Database Integration with SQLite + SQLAlchemy
=====================================================
⏱ 1.5 hrs | Builds on Days 8-9
 
THE PROBLEM WITH IN-MEMORY STORAGE:
When you restart your server, ALL your books disappear! 💨
A database saves data to a FILE on disk, so it survives restarts.
 
WHAT IS SQLite?
- A database that lives in a SINGLE FILE (e.g., books.db)
- No separate server to install — it's built into Python!
- Perfect for learning, prototyping, and small apps
- In production you'd use PostgreSQL, but the concepts are identical
 
WHAT IS SQLAlchemy?
- An ORM (Object-Relational Mapper)
- Instead of writing raw SQL: "SELECT * FROM books WHERE id = 1"
- You write Python: session.query(Book).filter(Book.id == 1).first()
- Your database tables become Python CLASSES
- Your rows become Python OBJECTS
 
WHAT IS AN ORM?
Think of it as a TRANSLATOR:
- You speak Python → ORM translates to SQL → Database understands
- Database returns data → ORM translates to Python objects → You understand
 
PROJECT STRUCTURE (we're getting organized now!):
    day10_database/
    ├── database.py    ← Database connection setup
    ├── models.py      ← SQLAlchemy table definitions
    ├── schemas.py     ← Pydantic models (request/response shapes)
    ├── crud.py        ← Database operations (Create, Read, Update, Delete)
    └── main.py        ← FastAPI app with endpoints
 
HOW TO RUN:
    pip install sqlalchemy
    cd day10_database
    uvicorn main:app --reload
"""