import os
from enum import Enum
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
import redis
import redis.asyncio as aioredis

from task_helpers.backends.async_ import AsyncBackend, AsyncRedisBackend
from task_helpers.backends.sync import Backend
from task_helpers.backends.sync import RedisBackend


@pytest.fixture(scope="session")
def mock_redis_client() -> Generator[redis.Redis, Any, None]:
    """Returns a Redis connection"""
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = int(os.environ.get("REDIS_PORT"))
    redis_db = int(os.environ.get("REDIS_DB"))
    redis_password = os.environ.get("REDIS_PASSWORD", None)

    assert redis_host is not None, "redis_host is None"
    assert redis_port is not None, "redis_port is None"
    assert redis_db is not None, "redis_db is None"

    connection = redis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=False)

    connection.flushdb()
    yield connection
    connection.close()
    connection.connection_pool.disconnect()


@pytest_asyncio.fixture
async def mock_aioredis_client() -> AsyncGenerator[aioredis.Redis, None]:
    """Create an async Redis client instance for testing using a separate database"""
    redis_host = os.environ.get("REDIS_HOST")
    redis_port = int(os.environ.get("REDIS_PORT"))
    redis_db = int(os.environ.get("REDIS_DB"))
    redis_password = os.environ.get("REDIS_PASSWORD", None)

    assert redis_host is not None, "redis_host is None"
    assert redis_port is not None, "redis_port is None"
    assert redis_db is not None, "redis_db is None"

    connection = aioredis.Redis(
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        decode_responses=False)

    yield connection
    await connection.close()
    await connection.connection_pool.disconnect()


class SyncBackendType(Enum):
    REDIS = RedisBackend


class AsyncBackendType(Enum):
    REDIS = AsyncRedisBackend


@pytest.fixture
def backend(request, mock_redis_client: redis.Redis) -> Backend:
    """Create a clean Backend instance for each test"""
    backend_type = request.param

    if backend_type == SyncBackendType.REDIS:
        mock_redis_client.flushdb()
        return RedisBackend(mock_redis_client)
    raise ValueError(f"Invalid backend type: {backend_type}")


@pytest_asyncio.fixture
async def async_backend(request, mock_aioredis_client: aioredis.Redis) -> AsyncBackend:
    """Create a clean AsyncBackend instance for each test"""
    backend_type = request.param

    if backend_type == AsyncBackendType.REDIS:
        await mock_aioredis_client.flushdb()
        return AsyncRedisBackend(mock_aioredis_client)
    raise ValueError(f"Invalid backend type: {backend_type}")


def pytest_generate_tests(metafunc):
    if "backend" in metafunc.fixturenames:
        metafunc.parametrize(
            "backend",
            list(SyncBackendType),
            indirect=True,
            ids=[backend_type.name for backend_type in SyncBackendType]
        )
    elif "async_backend" in metafunc.fixturenames:
        metafunc.parametrize(
            "async_backend",
            list(AsyncBackendType),
            indirect=True,
            ids=[backend_type.name for backend_type in AsyncBackendType]
        )
