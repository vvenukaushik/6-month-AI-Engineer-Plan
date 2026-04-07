"""
DAY 4 - EXERCISE 1: Async Fundamentals — Sequential vs Concurrent
===================================================================
AI Engineer Roadmap | Month 1
This file teaches you WHY async exists by showing the dramatic
difference between sequential and concurrent execution.
 
THE CORE IDEA:
    When your code waits for something (API response, file read, DB query),
    the CPU is doing NOTHING. Async lets Python do other work during that wait.
    
    Sequential:  Call API 1 → wait 2s → Call API 2 → wait 2s → Call API 3 → wait 2s = 6s total
    Concurrent:  Call APIs 1,2,3 simultaneously → wait 2s = 2s total (3x faster!)
 
WHY THIS MATTERS FOR AI ENGINEERING:
    - LLM API calls take 1-10 seconds each
    - RAG pipelines embed hundreds of documents (each = API call)
    - Agents make multiple tool calls that can run in parallel
    - Streaming responses require async generators
    Without async, your AI apps will be painfully slow."""

import aiohttp
import asyncio
import time

async def say_hello(name: str, delay: float) -> str:
    """
    An async function (coroutine).
    
    'async def' makes this a COROUTINE — it can be paused and resumed.
    'await' is where the pause happens: "pause me, do other work, come back when ready"
    
    KEY INSIGHT: asyncio.sleep() is the async version of time.sleep().
    - time.sleep(2) → blocks the ENTIRE program for 2 seconds
    - await asyncio.sleep(2) → pauses only THIS coroutine, others keep running
    """
    print(f"  [{name}] Starting... (will take {delay}s)")
    await asyncio.sleep(delay)
    print(f" [{name}] Done !")
    return f"Hello from {name}"

async def demo_sequential():
    """
    Run tasks one after another — like calling LLM APIs sequentially.
    Total time = sum of all delays.
    """
    print("\n🐌 SEQUENTIAL EXECUTION:")
    start = time.perf_counter()
    
    # Each await WAITS for the previous to finish before starting the next
    result1 = await say_hello("Task A", 1.0)
    result2 = await say_hello("Task B", 1.0)
    result3 = await say_hello("Task C", 1.0)
    
    elapsed = time.perf_counter() - start
    print(f"  Total time: {elapsed:.2f}s (≈3s because 1+1+1)")
    print(f"  Results: {[result1, result2, result3]}")
    return elapsed

async def demo_concurrent():
    """
    Run tasks simultaneously — like calling multiple LLM APIs at once.
    Total time = longest single task.
    """
    print("\n🚀 CONCURRENT EXECUTION (asyncio.gather):")
    start = time.perf_counter()
    
    # asyncio.gather() starts ALL coroutines simultaneously
    # and waits for ALL of them to complete
    results = await asyncio.gather(
        say_hello("Task A", 1.0),
        say_hello("Task B", 1.0),
        say_hello("Task C", 1.0),
    )
    
    elapsed = time.perf_counter() - start
    print(f"  Total time: {elapsed:.2f}s (≈1s because all ran in parallel)")
    print(f"  Results: {list(results)}")
    return elapsed

# ══════════════════════════════════════════════════════════════
# PART 2: Real HTTP calls — Sequential vs Concurrent
# ══════════════════════════════════════════════════════════════
 
# We use httpbin.org — a free service that returns test HTTP responses
# The /delay/N endpoint waits N seconds before responding (simulates slow APIs)

URLS = [
    "https://httpbin.org/delay/1",  # Responds after 1 second
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

async def fetch_url(session: aiohttp.ClientSession, url: str, label: str) -> dict:

    start = time.perf_counter()
    try:
       async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
           data = response.json()
           elapsed = time.perf_counter() - start
           print(f"    [{label}] ✅ {response.status} in {elapsed:.2f}s")
           return {"label": label, "status": response.status, "time": elapsed}
    except Exception as e:
        elapsed = time.perf_counter() - start
        print(f"    [{label}] ❌ Error: {e} in {elapsed:.2f}s")
        return {"label": label, "status": "error", "time": elapsed}

async def demo_concurrent_http():
    """Fetch 5 URLs simultaneously."""
    print("\n🚀 CONCURRENT HTTP CALLS (5 URLs at once):")
    start = time.perf_counter()
    
    async with aiohttp.ClientSession() as session:
        # Create all fetch tasks at once
        tasks = [
            fetch_url(session, url, f"Req {i+1}")
            for i, url in enumerate(URLS)
        ]
        # Run them ALL simultaneously
        results = await asyncio.gather(*tasks)
    
    elapsed = time.perf_counter() - start
    print(f"  Total: {elapsed:.2f}s")
    return elapsed

# ══════════════════════════════════════════════════════════════
# PART 3: asyncio.create_task — Fire and coordinate
# ══════════════════════════════════════════════════════════════

async def demo_create_task():
    '''asyncio.create_task() starts a coroutine in the BACKGROUND.
    Unlike gather(), you can do other work while it runs.
    
    AI usage: Start embedding documents in the background while
    you process the user's query.
    """
    print("\n🔧 asyncio.create_task() — Background execution:")'''

    async def background_job(name: str, seconds:float) -> str:
        print(f"    [{name}] Started in background")
        await asyncio.sleep(seconds)
        print(f"    [{name}] Completed!")
        return f"{name} result"
    
    start = time.perf_counter()
    task1 =  asyncio.create_task(background_job("Embed Doc A", 1.5))
    task2 = asyncio.create_task(background_job("Embed Doc B", 1.0))
    
    # Do other work while tasks run in the background
    print("    [Main] Doing other work while tasks run...")
    await asyncio.sleep(0.5)
    print("    [Main] Still working...")

    result1 = await task1
    result2 = await task2

    elapsed = time.perf_counter() - start
    print(f"    Results: {result1}, {result2}")
    print(f"    Total: {elapsed:.2f}s (main work overlapped with background tasks)")


# ══════════════════════════════════════════════════════════════
# PART 4: Error handling in async code
# ══════════════════════════════════════════════════════════════

async def demo_error_handling():
    """
    Async error handling patterns you'll need for LLM API calls.
    
    Critical pattern: when using gather(), one failure shouldn't
    crash everything. Use return_exceptions=True to handle gracefully.
    """

    print("\n🛡️  ERROR HANDLING in async code:")
    
    async def might_fail(name: str, should_fail: bool) -> str:
        await asyncio.sleep(0.3)
        if should_fail:
            raise ConnectionError(f"{name}: API connection refused")
        return f"{name}: success"
    
    results = await asyncio.gather(
        might_fail("Call 1", False),
        might_fail("call 2", True),
        might_fail("Call3", False),
        return_exceptions=True,
    )

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f" Call {i+1}: {type(result).__name__}: {result}")
        else:
            print(f" call {i+1}: {result}")

    # ── Pattern 2: Individual try/except ───────────────────
    print("\n  Pattern 2: Individual error handling per task")
    
    async def safe_call(name: str, should_fail: bool) -> dict:
        """Wraps each call with its own error handling."""
        try:
            result = await might_fail(name, should_fail)
            return {"status": "success", "result": result}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    results = await asyncio.gather(
        safe_call("Call A", False),
        safe_call("Call B", True),
        safe_call("Call C", False),
    )
    
    for r in results:
        icon = "✅" if r["status"] == "success" else "❌"
        value = r.get("result") or r.get("error")
        print(f"    {icon} {value}")


# ══════════════════════════════════════════════════════════════
# PART 5: Async generators — Streaming pattern
# ══════════════════════════════════════════════════════════════
 
async def demo_async_generator():
    """
    Async generators combine generators (yield) with async (await).
    
    This is EXACTLY how LLM streaming works:
    - The API sends tokens one at a time
    - Your code receives them via an async generator
    - You display each token immediately (no waiting for full response)
    
    In Month 2, you'll use this pattern with OpenAI and Anthropic's
    streaming APIs.
    """
    print("\n📡 ASYNC GENERATORS — The LLM Streaming Pattern:")

    async def stream_llm_response(prompt: str):
        """
        Simulates a streaming LLM response.
        
        In real code, this would be:
            async for chunk in client.chat.completions.create(stream=True, ...):
                yield chunk.choices[0].delta.content
        """
        response_words = f"Machine learning is a branch of AI that enables computers to learn from data without being explicitly programmed".split()

        for word in response_words:
            await asyncio.sleep(0.08)
            yield word + " "

    # ── Consume the stream ─────────────────────────────────
    print(f"  Prompt: 'What is machine learning?'")
    print(f"  Response: ", end="", flush=True)
    
    full_response = ""
    async for token in stream_llm_response("What is Machine Learning ?"):
        full_response += token

    print(f"\n  (Streamed {len(full_response.split())} words)")

    print(f"\n  Simulating 3 parallel LLM calls with streaming:")
    
    async def stream_with_label(label: str, words: list[str]):
        """Stream words with a label."""
        result = ""
        for word in words:
            await asyncio.sleep(0.05)
            result += word + " "
        return f"[{label}] {result.strip()}"
    
    results = await asyncio.gather(
        stream_with_label("Summary", ["AI", "is", "transforming", "industries"]),
        stream_with_label("Tweet", ["ML", "is", "the", "future!"]),
        stream_with_label("Title", ["Understanding", "Machine", "Learning"]),
    )
    for r in results:
        print(f"    {r}")



# ══════════════════════════════════════════════════════════════
# MAIN — Run all demos
# ══════════════════════════════════════════════════════════════
 
async def main():
    print("=" * 60)
    print("DAY 4: ASYNC PYTHON FUNDAMENTALS")
    print("=" * 60)
    
    # Part 1: Basic sequential vs concurrent
    seq_time = await demo_sequential()
    conc_time = await demo_concurrent()
    speedup = seq_time / conc_time if conc_time > 0 else 0
    print(f"\n  ⚡ Speedup: {speedup:.1f}x faster with concurrency!")
    
    # Part 2: Real HTTP calls (comment out if no internet)
    print("\n" + "=" * 60)
    print("REAL HTTP CALLS (using httpbin.org)")
    print("=" * 60)
    
    try:
        #seq_http = await demo_sequential_http()
        conc_http = await demo_concurrent_http()
        #speedup = seq_http / conc_http if conc_http > 0 else 0
        print(f"\n  ⚡ HTTP Speedup: {speedup:.1f}x faster!")
    except Exception as e:
        print(f"\n  ⚠️  HTTP demo skipped (network error: {e})")
        print("  This is fine — the concept is the same as Part 1")
    
    # Part 3: create_task
    print("\n" + "=" * 60)
    print("BACKGROUND TASKS")
    print("=" * 60)
    await demo_create_task()
    
    # Part 4: Error handling
    print("\n" + "=" * 60)
    print("ERROR HANDLING")
    print("=" * 60)
    await demo_error_handling()
    
    # Part 5: Async generators (streaming)
    print("\n" + "=" * 60)
    print("ASYNC GENERATORS (STREAMING)")
    print("=" * 60)
    await demo_async_generator()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎓 KEY TAKEAWAYS")
    print("=" * 60)
    print("  1. 'async def' creates a coroutine — it can be paused with 'await'")
    print("  2. 'await' pauses ONE coroutine, lets OTHERS run (not blocking)")
    print("  3. asyncio.gather() = run multiple coroutines concurrently")
    print("  4. asyncio.create_task() = start a coroutine in the background")
    print("  5. return_exceptions=True = don't crash if one task fails")
    print("  6. 'async for' + 'async generators' = streaming pattern (Month 2)")
    print("  7. aiohttp = async HTTP client (use instead of requests)")
 
 
if __name__ == "__main__":
    asyncio.run(main())