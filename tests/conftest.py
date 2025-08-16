import asyncio
import functools
import pickle
import random
import string
import threading
import time
import uuid
from typing import Callable, Type, Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
import redis
import redis.asyncio as aioredis

from task_helpers.compressors.core.base import LeveledCompressor, Compressor
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.serializers.base import Serializer
from task_helpers.serializers.custom_type import CustomTypeSerializer
from task_helpers.serializers.task import TaskSerializer
from task_helpers.tasks import Task


@pytest.fixture
def sample_data() -> bytes:
    """Returns repeating test data with a known pattern"""
    return b"test data" * 1000


@pytest.fixture
def random_text_generator(min_length: int = 10, max_length: int = 100) -> Callable[[], str]:
    """
    Returns a function that generates random text strings
    """

    def _generate() -> str:
        length = random.randint(min_length, max_length)
        return "".join(random.choice(string.ascii_letters) for _ in range(length))

    return _generate


@pytest.fixture
def random_text(random_text_generator) -> str:
    """
    Returns a single random text string
    """
    return random_text_generator()


@pytest.fixture()
def mock_compressor_class() -> Type[Compressor]:
    """
    Returns a mock compressor class that doesn't modify data
    """

    class MockCompressor(Compressor):
        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return MockCompressor


@pytest.fixture()
def mock_compressor(mock_compressor_class: Type[Compressor]) -> Compressor:
    """
    Returns a mock compressor that doesn't modify data
    """
    return mock_compressor_class()


@pytest.fixture()
def mock_leveled_compressor_class() -> Type[LeveledCompressor]:
    """
    Returns a mock-leveled compressor class that doesn't modify data
    """

    class MockLeveledCompressor(LeveledCompressor):
        MINIMAL_COMPRESSION_LEVEL = 1
        MEDIUM_COMPRESSION_LEVEL = 5
        MAXIMAL_COMPRESSION_LEVEL = 9

        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return MockLeveledCompressor


@pytest.fixture()
def mock_leveled_compressor(mock_leveled_compressor_class: Type[LeveledCompressor]) -> LeveledCompressor:
    """
    Returns a mock-leveled compressor that doesn't modify data
    """
    compression_level = mock_leveled_compressor_class.MEDIUM_COMPRESSION_LEVEL
    return mock_leveled_compressor_class(compression_level)


class MockSerializer(Serializer[str, bytes]):
    def serialize(self, data: str) -> bytes:
        return data.encode("utf-8")

    def deserialize(self, data: bytes) -> str:
        return data.decode("utf-8")


@pytest.fixture
def mock_task_serializer(mock_task_tuple_converter, mock_bytes_converter, mock_compressor) -> TaskSerializer:
    return TaskSerializer(
        tuple_converter=mock_task_tuple_converter,
        bytes_converter=mock_bytes_converter,
        compressor=mock_compressor,
    )


@pytest.fixture
def mock_task_result_serializer(mock_bytes_converter, mock_compressor) -> CustomTypeSerializer:
    return CustomTypeSerializer(
        bytes_converter=mock_bytes_converter,
        compressor=mock_compressor,
    )


class MockTaskTupleConverter(TaskTupleConverter):
    def encode(self, source: Task) -> tuple[bytes, Any]:
        return source.id.bytes, source.data

    def decode(self, target: tuple[bytes, Any]) -> Task:
        task_id = uuid.UUID(bytes=target[0])
        return Task(id=task_id, data=target[1])


@pytest.fixture
def mock_task_tuple_converter() -> TaskTupleConverter:
    return MockTaskTupleConverter()


class BytesConverterMock(BytesConverter):
    def encode(self, source) -> bytes:
        return pickle.dumps(source)

    def decode(self, target: bytes) -> Any:
        return pickle.loads(target)


@pytest.fixture
def mock_bytes_converter() -> BytesConverter:
    return BytesConverterMock()


@pytest.fixture(scope="session")
def mock_redis_client() -> Generator[redis.Redis, Any, None]:
    """Returns a Redis connection"""
    connection = redis.Redis(decode_responses=False, db=1)
    connection.flushdb()
    yield connection
    connection.close()
    connection.connection_pool.disconnect()


@pytest_asyncio.fixture
async def mock_aioredis_client() -> AsyncGenerator[aioredis.Redis, None]:
    """Create an async Redis client instance for testing using a separate database"""
    client = aioredis.Redis(db=1)
    yield client
    await client.close()
    await client.connection_pool.disconnect()


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
