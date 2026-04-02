import time
import functools
import random


def timer(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, *kwargs)
        elapsed = time.perf_counter() - start

        print(f" {func.__name__} () took {elapsed: .4f} seconds")

        return result
    return wrapper


def retry(max_attempts: int = 3, delay :float = 1.0, backoff: float = 2.0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_excpetion = None

            for attempt in range(1, max_attempts +1):
                try:
                    result = func(*args, *kwargs)
                    if attempt > 1:
                        print(f"{func.__name}() succeeded on attempt {attempt}")
                    return result
                except Exception as e:
                    last_excpetion = e
                    if attempt < max_attempts:
                        print(f" {func.__name__}() attempt {attempt}/{max_attempts} failed: {e}")
                        print(f"   Retrying in {current_delay:.1f}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        print(f" {func.__name__}() failed after {max_attempts} attempts")
            raise last_excpetion
        return wrapper
    return decorator


if __name__ == "__main__":
    print("=" * 60)
    print("DECORATOR 1: @timer")
    print("=" * 60)

    @timer
    def slow_operation():
        """Simulates a slow operation (like an LLM API call)."""
        time.sleep(0.5)
        return "Operation complete!"
    result = slow_operation()
    print(result)
    print()

