"""CLI Interface — The user-facing layer.
 
This is the ENTRY POINT of the application. Users interact with it like:
    python cli.py add --amount 42.50 --category food --description "Lunch"
    python cli.py list --category food
    python cli.py summary
    python cli.py delete --id abc123
    python cli.py export --format csv --output expenses.csv
 
CONCEPTS USED:
  - argparse           → Parsing command-line arguments
  - Dispatch table      → Dictionary mapping commands to handler functions
  - Type hints          → Every function is fully typed
  - Decorators          → @log_operation on command handlers
  - Custom exceptions   → Caught at the top level for clean error messages
 
ARCHITECTURE:
  This file NEVER imports json or touches files directly.
  It only talks to ExpenseStore. This is the "separation of concerns"
  principle — each layer has one job.
"""
 
import argparse
import sys
from datetime import date, datetime
from typing import Optional
 
from exceptions import ExpenseTrackerError, InvalidCategoryError
from logger import log_operation
from models import Category, Expense
from storage import ExpenseStore
# ══════════════════════════════════════════════════════════════════
# COMMAND DISPATCH TABLE
# ══════════════════════════════════════════════════════════════════
 
# This dictionary maps command names to their handler functions.
# It's the same pattern used in AI agent tool routing!
#
# Instead of:
#   if command == "add": cmd_add(...)
#   elif command == "list": cmd_list(...)
#   elif command == "summary": cmd_summary(...)
#
# We do:
#   handler = COMMANDS[command]
#   handler(store, args)
#
# This is cleaner, extensible, and the same pattern you'll see
# in FastAPI, Django, Flask, and AI agent frameworks.

COMMANDS = {
    "add": cmd_add,
    "list": cmd_list,
    "summary": cmd_summary,
    "delete": cmd_delete,
    "export": cmd_export,
}

# ══════════════════════════════════════════════════════════════════
# ARGUMENT PARSER — Defines what CLI arguments are accepted
# ══════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands.
 
    argparse handles:
    - Parsing command-line strings into Python objects
    - Generating --help text automatically
    - Validating required arguments
    - Type conversion (e.g., --amount "42.5" → float 42.5)
    """
    parser = argparse.ArgumentParser(
        description="💰 CLI Expense Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py add --amount 42.50 --category food --description "Lunch"
  python cli.py list --category food
  python cli.py list --start 2025-01-01 --end 2025-01-31
  python cli.py summary
  python cli.py export --format csv --output my_expenses.csv
  python cli.py delete --id abc123
        """,
    )
 
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
    )
 
    # ── ADD ───────────────────────────────────────────────────────
    add_p = subparsers.add_parser("add", help="Add a new expense")
    add_p.add_argument(
        "--amount", type=float, required=True,
        help="Amount in dollars (must be positive)",
    )
    add_p.add_argument(
        "--category", type=str, required=True,
        choices=[c.value for c in Category],
        help=f"Category: {', '.join(c.value for c in Category)}",
    )
    add_p.add_argument(
        "--description", type=str, required=True,
        help="What was this expense for?",
    )
    add_p.add_argument(
        "--date", type=str, default=None,
        help="Date in YYYY-MM-DD format (defaults to today)",
    )
    add_p.add_argument(
        "--tags", type=str, default="",
        help="Comma-separated tags (e.g., 'work,commute')",
    )


    # ── LIST ──────────────────────────────────────────────────────
    list_p = subparsers.add_parser("list", help="List expenses")
    list_p.add_argument("--category", type=str, default=None, help="Filter by category")
    list_p.add_argument("--start", type=str, default=None, help="Start date (YYYY-MM-DD)")
    list_p.add_argument("--end", type=str, default=None, help="End date (YYYY-MM-DD)")
    list_p.add_argument("--tag", type=str, default=None, help="Filter by tag")
 
    # ── SUMMARY ───────────────────────────────────────────────────
    subparsers.add_parser("summary", help="Show expense summary with chart")
 
    # ── DELETE ────────────────────────────────────────────────────
    del_p = subparsers.add_parser("delete", help="Delete an expense")
    del_p.add_argument("--id", type=str, required=True, help="Expense ID to delete")
 
    # ── EXPORT ────────────────────────────────────────────────────
    exp_p = subparsers.add_parser("export", help="Export expenses")
    exp_p.add_argument(
        "--format", type=str, choices=["csv", "json"],
        default="csv", help="Export format (default: csv)",
    )
    exp_p.add_argument(
        "--output", type=str, default=None,
        help="Output file path",
    )
 
    return parser
 
