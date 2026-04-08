"""
DAY 4 - EXERCISE 2: Async Rate Limiter
========================================
AI Engineer Roadmap | Month 1, Week 1

When calling LLM APIs concurrently, you can't fire 100 requests at once.
APIs have rate limits (e.g., OpenAI: 500 requests/minute for GPT-4).
You need to CONTROL the concurrency.

This file teaches three rate limiting patterns:
  1. Semaphore — max N concurrent requests
  2. Token bucket — max N requests per time window
  3. Practical pattern — combining both for production use

WHY THIS MATTERS:
    In Month 2, you'll call OpenAI/Anthropic APIs hundreds of times.
    In Month 3, you'll embed hundreds of document chunks.
    Without rate limiting, you'll get 429 errors and your app crashes.
    With rate limiting, everything flows smoothly.

HOW TO RUN:
    python day4_rate_limiter.py
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


# ══════════════════════════════════════════════════════════════
# PATTERN 1: Semaphore — Max N concurrent tasks
# ══════════════════════════════════════════════════════════════

async def demo_semaphore():
    """
    asyncio.Semaphore limits how many coroutines run AT THE SAME TIME.
    
    Think of it like a bouncer at a club:
    - Club capacity = 3 (the semaphore value)
    - When 3 people are inside, the next person WAITS at the door
    - When someone leaves, the next person in line enters
    
    Without semaphore: all 10 tasks start at once → API rate limit hit
    With semaphore(3): max 3 tasks run at once → smooth execution
    """
    print("=" * 60)
    print("PATTERN 1: Semaphore (max concurrent tasks)")
    print("=" * 60)
    
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent
    
    async def limited_api_call(task_id: int) -> str:
        """An API call that respects the semaphore limit."""
        async with semaphore:  # Acquire slot (waits if 3 are already running)
            start = time.perf_counter()
            print(f"  [{task_id:2d}] 🟢 Started  (active tasks: {3 - semaphore._value}/3)")
            await asyncio.sleep(0.5)  # Simulate API call
            elapsed = time.perf_counter() - start
            print(f"  [{task_id:2d}] 🔵 Finished ({elapsed:.2f}s)")
            return f"Result from task {task_id}"
        # Semaphore is released automatically when exiting 'async with'
    
    start = time.perf_counter()
    
    # Launch 10 tasks — but only 3 run at a time
    tasks = [limited_api_call(i) for i in range(1, 11)]
    results = await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start
    print(f"\n  Completed {len(results)} tasks in {elapsed:.2f}s")
    print(f"  Without semaphore: ~0.5s (all at once)")
    print(f"  With semaphore(3): ~{0.5 * (10/3):.1f}s (batches of 3)")


# ══════════════════════════════════════════════════════════════
# PATTERN 2: Token Bucket — N requests per time window
# ══════════════════════════════════════════════════════════════

class TokenBucketRateLimiter:
    """
    Token bucket algorithm: allows N requests per time period.
    
    How it works:
    - Bucket starts full with 'max_tokens' tokens
    - Each request consumes 1 token
    - Tokens refill at 'refill_rate' per second
    - If bucket is empty → wait until a token is available
    
    Real-world mapping:
    - OpenAI: ~500 requests/minute → max_tokens=500, refill_rate=8.33/sec
    - Anthropic: varies by tier
    
    This is more sophisticated than a semaphore because it controls
    the RATE (requests per second) not just the concurrency.
    """
    
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Args:
            max_tokens: Maximum burst capacity
            refill_rate: Tokens added per second
        """
        self.max_tokens = max_tokens
        self.tokens = max_tokens
        self.refill_rate = refill_rate
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Wait until a token is available, then consume it."""
        while True:
            async with self._lock:
                self._refill()
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
            # No tokens available — wait a bit and try again
            await asyncio.sleep(0.05)
    
    def _refill(self) -> None:
        """Add tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now


async def demo_token_bucket():
    """Demo: Process 15 tasks at max 5 per second."""
    print("\n" + "=" * 60)
    print("PATTERN 2: Token Bucket (requests per second)")
    print("=" * 60)
    
    # Allow 5 requests per second, burst up to 5
    limiter = TokenBucketRateLimiter(max_tokens=5, refill_rate=5.0)
    
    async def rate_limited_call(task_id: int) -> str:
        await limiter.acquire()  # Wait for a token
        timestamp = time.perf_counter()
        print(f"  [{task_id:2d}] Executed at t={timestamp % 100:.2f}s "
              f"(tokens remaining: {limiter.tokens:.1f})")
        await asyncio.sleep(0.1)  # Quick API call
        return f"Done {task_id}"
    
    start = time.perf_counter()
    tasks = [rate_limited_call(i) for i in range(1, 16)]
    results = await asyncio.gather(*tasks)
    elapsed = time.perf_counter() - start
    
    print(f"\n  Completed {len(results)} tasks in {elapsed:.2f}s")
    print(f"  Rate: ~{len(results)/elapsed:.1f} requests/sec (target: 5/sec)")


# ══════════════════════════════════════════════════════════════
# PATTERN 3: Production Rate Limiter (combines both patterns)
# ══════════════════════════════════════════════════════════════

@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    max_concurrent: int = 5          # Max simultaneous requests
    max_per_second: float = 10.0     # Max requests per second
    max_retries: int = 3             # Retry on rate limit errors
    retry_base_delay: float = 1.0    # Base delay for exponential backoff


class ProductionRateLimiter:
    """
    Production-grade rate limiter combining:
    1. Semaphore for concurrency control
    2. Token bucket for rate control
    3. Retry with exponential backoff for 429 errors
    
    This is essentially what you'd use in a real AI application.
    Libraries like 'tenacity' and 'aiolimiter' provide similar functionality,
    but understanding the internals helps you debug issues.
    """
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.bucket = TokenBucketRateLimiter(
            max_tokens=int(config.max_per_second),
            refill_rate=config.max_per_second,
        )
        self.total_requests = 0
        self.total_retries = 0
        self.total_failures = 0
    
    async def execute(self, func: Callable, *args: Any, **kwargs: Any) -> Any:
        """
        Execute a function with rate limiting and retry logic.
        
        Usage:
            limiter = ProductionRateLimiter(config)
            result = await limiter.execute(call_openai, prompt="Hello")
        """
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):
            # Wait for both: concurrency slot AND rate limit token
            async with self.semaphore:
                await self.bucket.acquire()
                self.total_requests += 1
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    last_error = e
                    self.total_retries += 1
                    
                    if attempt < self.config.max_retries:
                        delay = self.config.retry_base_delay * (2 ** (attempt - 1))
                        print(f"    ⚠️  Attempt {attempt} failed: {e}. "
                              f"Retrying in {delay:.1f}s...")
                        await asyncio.sleep(delay)
                    else:
                        self.total_failures += 1
                        print(f"    ❌ All {self.config.max_retries} attempts failed: {e}")
        
        raise last_error
    
    def get_stats(self) -> dict:
        """Return rate limiter statistics."""
        return {
            "total_requests": self.total_requests,
            "total_retries": self.total_retries,
            "total_failures": self.total_failures,
        }


async def demo_production_limiter():
    """Demo: Production rate limiter with retries."""
    print("\n" + "=" * 60)
    print("PATTERN 3: Production Rate Limiter")
    print("=" * 60)
    
    config = RateLimitConfig(
        max_concurrent=3,
        max_per_second=5.0,
        max_retries=3,
        retry_base_delay=0.5,
    )
    limiter = ProductionRateLimiter(config)
    
    call_count = 0
    
    async def simulate_api_call(task_id: int) -> str:
        """Simulates an API that sometimes fails with rate limiting."""
        nonlocal call_count
        call_count += 1
        
        await asyncio.sleep(0.2)  # Simulate network latency
        
        # Every 4th call fails (simulates rate limiting)
        if call_count % 4 == 0:
            raise ConnectionError(f"429: Rate Limited (task {task_id})")
        
        return f"Task {task_id}: Success"
    
    start = time.perf_counter()
    
    # Run 12 tasks through the production limiter
    tasks = [limiter.execute(simulate_api_call, i) for i in range(1, 13)]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    elapsed = time.perf_counter() - start
    
    successes = sum(1 for r in results if isinstance(r, str))
    failures = sum(1 for r in results if isinstance(r, Exception))
    
    print(f"\n  📊 Results:")
    print(f"     Completed: {successes}/{len(results)}")
    print(f"     Failed: {failures}/{len(results)}")
    print(f"     Stats: {limiter.get_stats()}")
    print(f"     Total time: {elapsed:.2f}s")


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

async def main():
    await demo_semaphore()
    await demo_token_bucket()
    await demo_production_limiter()
    
    print("\n" + "=" * 60)
    print("🎓 KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. Semaphore: controls HOW MANY tasks run at once")
    print("  2. Token bucket: controls HOW FAST tasks execute (rate)")
    print("  3. Production apps need BOTH + retry with backoff")
    print("  4. asyncio.Semaphore is the simplest to start with")
    print("  5. Always use return_exceptions=True in gather() for resilience")
    print("  6. These patterns are used in every AI app that calls external APIs")


if __name__ == "__main__":
    asyncio.run(main())