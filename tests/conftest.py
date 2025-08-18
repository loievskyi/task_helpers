import asyncio
import functools
import random
import string
import threading
import time
from typing import Callable

import pytest


@pytest.fixture
def random_text_generator(min_length: int = 10, max_length: int = 100) -> Callable[[], str]:
    """
    Returns a function that generates random text strings
    """

    def _generate() -> str:
        length = random.randint(min_length, max_length)
        chars = string.ascii_letters
        return "".join(random.choice(chars) for _ in range(length))

    return _generate


@pytest.fixture
def random_text(random_text_generator) -> str:
    """
    Returns a single random text string
    """
    return random_text_generator()


def assert_blocks_longer_than(seconds: float, timeout: float = None):
    """
    Decorator to assert that a synchronous function blocks for at least `seconds`.

    Parameters:
    - seconds: Minimum time the function should block.
    - timeout: Maximum time to wait for the function to finish. Prevents test from hanging forever.
               If not set, defaults to `seconds + 1`.

    Raises:
    - AssertionError if the function completes before `seconds` seconds.
    """
    if timeout is None:
        timeout = seconds + 1

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.daemon = True
            start = time.perf_counter()
            thread.start()

            # Wait only for the minimum expected blocking time
            thread.join(timeout=seconds)
            duration = time.perf_counter() - start

            if not thread.is_alive():
                raise AssertionError(
                    f"Function returned too early: {duration:.2f} seconds (expected > {seconds})"
                )

            # Optionally give it a little more time to finish, to avoid hanging the test
            thread.join(timeout=(timeout - seconds))

        return wrapper

    return decorator


def assert_async_blocks_longer_than(seconds: float, timeout: float = None):
    """
    Decorator to assert that an async function blocks for at least `seconds`.

    Parameters:
    - seconds: Minimum expected blocking time.
    - timeout: Maximum wait time before cancelling (defaults to seconds + 1).

    Raises:
    - AssertionError if the function finishes earlier than expected.
    """
    if timeout is None:
        timeout = seconds + 1

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            task = asyncio.create_task(func(*args, **kwargs))
            start = time.perf_counter()

            try:
                # If a function returns too quickly — it's an error
                await asyncio.wait_for(task, timeout=seconds)
                duration = time.perf_counter() - start
                raise AssertionError(
                    f"Function returned too early: {duration:.2f} seconds (expected > {seconds})"
                )
            except asyncio.TimeoutError:
                # Good: function did not finish within `seconds`
                pass

            duration = time.perf_counter() - start
            assert duration >= seconds, f"Function returned too early: {duration:.2f} seconds"

            # Cancel the task to avoid hanging
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=timeout - seconds)
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                pass

        return wrapper

    return decorator
