from contextlib import contextmanager
from typing import Type, Generator

import redis

from task_helpers.exceptions import DoesNotExistError
from .base import Backend


class RedisBackend(Backend):
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def get(self, key: str) -> bytes:
        """Get value by key"""
        result: bytes | None = self.redis_client.get(key)
        if result is None:
            raise DoesNotExistError
        return result

    def set(self, key: str, value: bytes) -> None:
        """Set a key-value pair"""
        self.redis_client.set(key, value)

    def add_to_queue(self, queue_name: str, data: bytes) -> None:
        """Add single item to queue"""
        self.redis_client.rpush(queue_name, data)

    def bulk_add_to_queue(self, queue_name: str, data: list[bytes]) -> None:
        """Add multiple items to queue"""
        self.redis_client.rpush(queue_name, *data)

    def pop_from_queue(self, queue_name: str, error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop single item from queue"""
        result: bytes | None = self.redis_client.lpop(queue_name)  # returns bytes or None
        if result is None:
            raise error_class
        return result

    def pop_from_queue_blocking(self, queue_name: str, timeout_seconds: int | None = None) -> bytes:
        """Pop single item from queue with blocking"""
        result = self.redis_client.blpop([queue_name], timeout=timeout_seconds)  # returns tuple (queue_name, value) or None
        if result is None:
            raise TimeoutError
        return result[1]

    def bulk_pop_from_queue(self, queue_name: str, max_count: int) -> list[bytes]:
        """Pop multiple items from queue"""
        result = self.redis_client.lpop(queue_name, count=max_count)  # returns a list of results or None
        if not result:
            return []
        return result

    def move_between_queues(
        self,
        source_queue_name: str,
        target_queue_name: str,
        error_class: Type[DoesNotExistError] = DoesNotExistError
    ) -> bytes:
        """Move a single item between queues"""
        result: bytes | None = self.redis_client.lmove(source_queue_name, target_queue_name)
        if result is None:
            raise error_class
        return result

    def move_between_queues_blocking(
        self,
        source_queue_name: str,
        target_queue_name: str,
        timeout_seconds: int | None = None
    ) -> bytes:
        """Move a single item between queues with blocking"""
        timeout_seconds = timeout_seconds or 0  # 0 means infinite wait
        result: bytes | None = self.redis_client.blmove(
            source_queue_name,
            target_queue_name,
            timeout=timeout_seconds
        )
        if result is None:
            raise TimeoutError
        return result

    def pop_or_requeue(
        self,
        queue_name: str,
        delete_data: bool = True,
        error_class: Type[DoesNotExistError] = DoesNotExistError
    ) -> bytes:
        """Pop item from queue or move it back to the same queue"""
        if delete_data:
            return self.pop_from_queue(queue_name, error_class)
        else:
            return self.move_between_queues(queue_name, queue_name, error_class)

    def pop_or_requeue_blocking(
        self,
        queue_name: str,
        delete_data: bool = True,
        timeout_seconds: int | None = None
    ) -> bytes:
        """Pop item from queue or move it back to the same queue with blocking"""
        if delete_data:
            return self.pop_from_queue_blocking(queue_name, timeout_seconds)
        else:
            return self.move_between_queues_blocking(queue_name, queue_name, timeout_seconds)

    def exists(self, key: str) -> bool:
        """Check if the key exists"""
        return bool(self.redis_client.exists(key))

    def expire(self, key: str, seconds: int) -> None:
        """Set a key expiration time"""
        self.redis_client.expire(key, seconds)

    @contextmanager
    def pipeline(self) -> Generator["RedisBackend", None, None]:
        """Create a Redis pipeline for atomic operations"""
        pipeline = self.redis_client.pipeline()
        try:
            yield self.__class__(pipeline)
        finally:
            pipeline.execute()
