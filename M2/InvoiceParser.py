"""
Invoice Parser — Structured Outputs Practice Exercise
======================================================
 
Goal: Parse messy, real-world invoice text into clean structured data
using Instructor + Pydantic + Anthropic (Claude).
 
Setup:
    pip install instructor anthropic pydantic python-dotenv
 
    Then set your API key:
        export ANTHROPIC_API_KEY="sk-ant-your-key-here"
    Or create a .env file:
        ANTHROPIC_API_KEY=sk-ant-your-key-here
 
What you'll learn:
    1. Defining Pydantic models with Field descriptions
    2. Using Instructor with Anthropic/Claude
    3. Handling optional/missing fields without hallucination
    4. Validation with custom Pydantic validators
    5. Retry logic for self-healing extraction
    6. Edge cases: ambiguous dates, missing data, multiple items
"""

import instructor
from pydantic import BaseModel, Field, field_validator
from anthropic import Anthropic
from typing import Optional
from datetime import datetime, date
from dotenv import load_dotenv

load_dotenv()


# =============================================================================
# STEP 1: Define Your Schema
# =============================================================================
# This is where you tell the model EXACTLY what shape you want.
# Key principle: The more specific your Field descriptions, the better
# the extraction. Especially for optional fields — always tell the model
# when to return null.

class LineItem(BaseModel):
    description: str = Field(
        description="Name or description of the item"
    )
    quantity: int = Field(
        default=1,
        description="Number of this item. Default to 1 if not specified."
    )
    unit_price: Optional[int] = Field(
        default=0,
        description="Price per unit. Set to null if only a total is given "
                    "and individual prices cannot be determined."
    )

    @field_validator("quantity")
    @classmethod
    def validate_unit(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be positive integer")
        return v
    

class Invoice(BaseModel):
    """Structured representation of an invoice."""
    invoice_number: str = Field(
        description="The invoice ID/number (e.g., '123', 'A-447'). "
                    "Include any prefixes like '#' or 'INV-'."
    )
    amount: float = Field(
        description="Total amount in USD."
    )
    items: list[LineItem] = Field(
        description="List of line items on the invoice."
    )
    due_date: Optional[date] = Field(
        default=None,
        description="Payment due date. Set to null if no due date is "
                    "mentioned. Do NOT guess or infer a date."
    )
    currency: str = Field(
        default="USD",
        description="Currency code. Default to 'USD' unless another "
                    "currency is explicitly mentioned (e.g., EUR, GBP)."
    )
    confidence: float = Field(
        description="0.0 to 1.0 — how confident you are in the overall "
                    "extraction. Use lower values when fields are ambiguous, "
                    "missing, or had to be inferred."
    )
 
    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be positive.")
        return v
 
    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0.")
        return v
 
    

# =============================================================================
# STEP 2: Build the Parser Function
# =============================================================================
# This is the core function that takes raw text and returns structured data.
# Notice how the system prompt reinforces the "don't hallucinate" rule.


def parse_invoice(text: str) -> Invoice:
    """Parse raw invoice text into a structured Invoice object."""
    client = instructor.from_anthropic(Anthropic())
    
    invoice = client.messages.create(
        model = "claude-sonnet-4-6",
        max_tokens = 2800,
        response_model= Invoice,
        max_retries=2,
        messages=[
            {
                "role": "user", "content":(
                    "Extract the invoice information from the following text. "
                    "Only extract what is explicitly stated. "
                    "If a field is not mentioned, set it to null. "
                    "Never guess or infer missing values.\n\n"
                    f"Text: {text}"
                )
            }
        ]
    )

    return invoice


# =============================================================================
# STEP 3: Test with Various Inputs
# =============================================================================
# Good practice: test with clean input, messy input, and missing data.


def main():
    test_cases = [
        # Case 1: Clean, straightforward input
        {
            "name": "Clean input",
            "text": "Invoice #123, $45.99 for 3 widgets, due March 30 2025",
        },
 
        # Case 2: Multiple items
        {
            "name": "Multiple items",
            "text": (
                "INV-A447: 2 keyboards at $49.99 each, 1 mouse at $29.99, "
                "and a monitor for $299.00. Total: $428.97. "
                "Payment due by April 15, 2025."
            ),
        },
 
        # Case 3: Missing fields (no due date)
        {
            "name": "Missing due date",
            "text": "Invoice 9921 — $150.00 for consulting services (2 hours)",
        },
 
        # Case 4: Messy, informal text
        {
            "name": "Messy informal text",
            "text": (
                "hey, so that invoice for the 5 t-shirts and 10 stickers... "
                "it's invoice number 88B, total is like $74.50. "
                "Need it paid by end of next month I guess?"
            ),
        },
 
        # Case 5: Non-USD currency
        {
            "name": "Non-USD currency",
            "text": (
                "Facture #FR-2211. Montant: €1,250.00 pour 5 licences logiciel. "
                "Date d'échéance: 30 juin 2025."
            ),
        },
    ]
 
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {case['name']}")
        print(f"Input: {case['text']}")
        print(f"{'='*60}")
 
        try:
            result = parse_invoice(case["text"])
            print(f"  Invoice #:    {result.invoice_number}")
            print(f"  Amount:       {result.amount} {result.currency}")
            print(f"  Due Date:     {result.due_date or 'Not specified'}")
            print(f"  Confidence:   {result.confidence}")
            print(f"  Items:")
            for item in result.items:
                price_str = f" @ ${item.unit_price}" if item.unit_price else ""
                print(f"    - {item.quantity}x {item.description}{price_str}")
        except Exception as e:
            print(f"  ERROR: {e}")
 
 
if __name__ == "__main__":
    main()