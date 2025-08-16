from enum import Enum

import pytest
import pytest_asyncio
import redis
import redis.asyncio as aioredis

from task_helpers.backends.async_ import AsyncBackend, AsyncRedisBackend
from task_helpers.backends.sync import Backend
from task_helpers.backends.sync import RedisBackend


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
