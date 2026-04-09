'''DAY 6: CLI EXPENSE TRACKER — CLI INTERFACE (cli.py)
=============================================================================
SKILLS USED:
  Day 1: Decorators (@log_operation on every command)
  Day 2: OOP (store[id], len(store), iteration)
  Day 3: Type Hints + Pydantic (model creation & validation)
  Day 5: Exception handling (catch hierarchy) + Logging
 
WHY CLI DESIGN MATTERS FOR AI ENGINEERING:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every AI tool you'll use has a CLI:
  - `openai api chat.completions.create --model gpt-4 --prompt "..."`
  - `langchain serve` / `langchain app new my-app`
  - `chromadb run --host localhost --port 8000`
  - `mlflow server --backend-store-uri sqlite:///mlflow.db`
 
argparse is the standard library tool. Click and Typer are popular
alternatives (Typer uses type hints — very Pythonic). For this project,
argparse shows you the fundamentals.
 
ARCHITECTURE NOTE:
  This file is the CONTROLLER layer (MVC pattern):
    - Models (models.py) → data definitions
    - Storage (storage.py) → data access
    - CLI (cli.py) → user interface / controller
    - Exceptions → error handling across all layers
    - Logger → observability across all layers
 
  In Month 2, this same architecture becomes:
    - Models → Pydantic schemas for LLM tool calls
    - Storage → Vector store / document store
    - Controller → FastAPI endpoints or Agent orchestrator
============================================================================='''