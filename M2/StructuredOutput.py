import os
import instructor

from anthropic import Anthropic
from pydantic import BaseModel
from datetime import date

class Invoice(BaseModel):
    invoice_num: int
    amount: float
    items: list[str]
    due_date: date


client = instructor.from_anthropic(Anthropic())

invoice = client.messages.create(
    model = "claude-sonnet-4-6",
    max_tokens = 1024,
    response_model=Invoice,
    messages=[
        {"role": "user", "content": "Invoice #123, $45.99 for 3 widgets, due March 30"}
    ]
)

print(invoice.invoice_num)