from __future__ import annotations
from functools import total_ordering



#@total_ordering
class Money:


    def __init__(self, amount: float, currency: str):
        self.amount = amount
        self.currency = currency
    

    def __str__(self) -> str:
        
        return f"{self.amount:.2f} {self.currency}"
    
    def __repr__(self) -> str:
        
        return f"Money(amount = {self.amount:.2f} , currency = {self.currency})"
    
    def _check_currency(self, object: Money) -> None:
        if not isinstance(object, Money):
            raise TypeError(f"cannot operate on Monay {type(object).__name__}")
        
        if object.currency != self.currency:
            raise ValueError(f"Cannot combine {self.currency} , {object.currency}.")
        
    
    def __add__(self, other) -> Money:
        self._check_currency(other)
        #Returns a NEW Money object (doesn't modify self or other).
        #This is important — objects should generally be immutable in operations.
        return Money(self.currency + other.currency, self.currency)
    
    def __sub__(self, other) -> Money:
        self._check_currency(other)
        return Money(self.amount - other.amount, self.currency)
    
    def __mul__(self, factor: int | float) -> Money:
        if not isinstance(factor, (int, float)):
            raise TypeError(f"can only multiply with number not by {type(factor).__name__}")
        
        return Money(self.amount * factor, self.currency)
    
    def __rmul__(self, factor: int | float) -> Money:
        """
        Called when Money is on the RIGHT side: 3 * Money(10) → Money(30)
        
        Without this, Python doesn't know how to compute int * Money.
        __rmul__ is the "reflected" version of __mul__.
        """
        return self.__mul__(factor)
    
    
if __name__ == "__main__":
    print("=" * 60)
    print("MONEY CLASS — DUNDER METHODS DEMO")
    print("=" * 60)
    
    # ── Creating instances (__init__) ──────────────────────
    print("\n📦 Creating Money objects:")
    wallet = Money(100.00, "USD")
    coffee = Money(4.50, "USD")
    lunch = Money(12.75, "USD")
    print(f"   wallet = {wallet}")
    print(f"   coffee = {coffee}")
    print(f"   lunch  = {lunch}")
    
    # ── __str__ vs __repr__ ────────────────────────────────
    print("\n📝 __str__ vs __repr__:")
    print(f"   str(wallet)  = {str(wallet)}")       # Human-friendly
    print(f"   repr(wallet) = {repr(wallet)}")       # Developer-friendly
    
    # ── Arithmetic (__add__, __sub__, __mul__) ─────────────
    print("\n➕ Arithmetic:")
    remaining = wallet - coffee - lunch
    print(f"   {wallet} - {coffee} - {lunch} = {remaining}")
    
    total_coffees = coffee * 5
    print(f"   {coffee} × 5 = {total_coffees}")
    
    # __rmul__ lets the number come first
    also_coffees = 5 * coffee
    print(f"   5 × {coffee} = {also_coffees}")