from contextlib import asynccontextmanager
from typing import Type, AsyncGenerator

from redis import asyncio as aioredis

from task_helpers.exceptions import DoesNotExistError
from .base import AsyncBackend


class AsyncRedisBackend(AsyncBackend):
    def __init__(self, redis_client: aioredis.Redis):
        self.redis_client = redis_client

    async def get(self, key: str) -> bytes:
        """Get value by key"""
        result: bytes | None = await self.redis_client.get(key)
        if result is None:
            raise DoesNotExistError
        return result

    async def set(self, key: str, value: bytes) -> None:
        """Set a key-value pair"""
        await self.redis_client.set(key, value)

    async def add_to_queue(self, queue_name: str, data: bytes) -> None:
        """Add single item to queue"""
        await self.redis_client.rpush(queue_name, data)

    async def bulk_add_to_queue(self, queue_name: str, data: list[bytes]) -> None:
        """Add multiple items to queue"""
        await self.redis_client.rpush(queue_name, *data)

    async def pop_from_queue(self, queue_name: str, error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop single item from queue"""
        result: bytes | None = await self.redis_client.lpop(queue_name)
        if result is None:
            raise error_class
        return result

    async def pop_from_queue_blocking(self, queue_name: str, timeout_seconds: int | None = None) -> bytes:
        """Pop single item from queue with blocking"""
        result = await self.redis_client.blpop([queue_name], timeout=timeout_seconds)
        if result is None:
            raise TimeoutError
        return result[1]

    async def bulk_pop_from_queue(self, queue_name: str, max_count: int) -> list[bytes]:
        """Pop multiple items from queue"""
        result = await self.redis_client.lpop(queue_name, count=max_count)
        if not result:
            return []
        return result

    async def move_between_queues(
        self,
        source_queue_name: str,
        target_queue_name: str,
        error_class: Type[DoesNotExistError] = DoesNotExistError
    ) -> bytes:
        """Move a single item between queues"""
        result: bytes | None = await self.redis_client.lmove(source_queue_name, target_queue_name)
        if result is None:
            raise error_class
        return result

    async def move_between_queues_blocking(
        self,
        source_queue_name: str,
        target_queue_name: str,
        timeout_seconds: int | None = None
    ) -> bytes:
        """Move a single item between queues with blocking"""
        timeout_seconds = timeout_seconds or 0  # 0 means infinite wait
        result: bytes | None = await self.redis_client.blmove(
            source_queue_name,
            target_queue_name,
            timeout=timeout_seconds
        )
        if result is None:
            raise TimeoutError
        return result

    async def pop_or_requeue(
        self,
        queue_name: str,
        delete_data: bool = True,
        error_class: Type[DoesNotExistError] = DoesNotExistError
    ) -> bytes:
        """Pop item from queue or move it back to the same queue"""
        if delete_data:
            return await self.pop_from_queue(queue_name, error_class)
        else:
            return await self.move_between_queues(queue_name, queue_name, error_class)

    async def pop_or_requeue_blocking(
        self,
        queue_name: str,
        delete_data: bool = True,
        timeout_seconds: int | None = None
    ) -> bytes:
        """Pop item from queue or move it back to the same queue with blocking"""
        if delete_data:
            return await self.pop_from_queue_blocking(queue_name, timeout_seconds)
        else:
            return await self.move_between_queues_blocking(queue_name, queue_name, timeout_seconds)

    async def exists(self, key: str) -> bool:
        """Check if the key exists"""
        return bool(await self.redis_client.exists(key))

    async def expire(self, key: str, seconds: int) -> None:
        """Set a key expiration time"""
        await self.redis_client.expire(key, seconds)

    @asynccontextmanager
    async def pipeline(self) -> AsyncGenerator["AsyncRedisBackend", None]:
        """Create a Redis pipeline for atomic operations"""
        pipeline = self.redis_client.pipeline()
        try:
            yield self.__class__(pipeline)
        finally:
            await pipeline.execute()
