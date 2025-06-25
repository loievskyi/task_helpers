from typing import Type, Generator

import redis
from contextlib import contextmanager

from task_helpers.exceptions import DoesNotExistError


class RedisBackend:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    def get(self, key: str) -> bytes:
        result: bytes = self.redis_client.get(key)
        if result is None:
            raise DoesNotExistError
        return bytes(result)

    def set(self, key: str, value: bytes) -> None:
        self.redis_client.set(key, value)

    def add_to_queue(self, queue_name: str, data: bytes) -> None:
        self.redis_client.rpush(queue_name, data)

    def bulk_add_to_queue(self, queue_name: str, data: list[bytes]) -> None:
        self.redis_client.rpush(queue_name, *data)

    def pop_from_queue(self, queue_name: str, error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        result = self.redis_client.lpop(queue_name)  # returns bytes or None
        if result is None:
            raise error_class
        return bytes(result)

    def bulk_pop_from_queue(self, queue_name: str, count: int) -> list[bytes]:
        result = self.redis_client.lpop(queue_name, count=count)  # returns a list of results or None
        if not result:
            return []
        return result

    def move_between_queues(self, source_queue_name: str, target_queue_name: str,
                            error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        result: bytes | None = self.redis_client.lmove(source_queue_name, target_queue_name)
        if result is None:
            raise error_class
        return result

    def pop_or_requeue(self, queue_name: str,
                       delete_data=True,
                       error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        if delete_data:
            return self.pop_from_queue(queue_name, error_class)
        else:
            return self.move_between_queues(queue_name, queue_name,
                                            error_class)

    def exists(self, key: str) -> bool:
        return bool(self.redis_client.exists(key))

    def expire(self, key: str, seconds: int) -> None:
        self.redis_client.expire(key, seconds)

    @contextmanager
    def pipeline(self) -> Generator["RedisBackend", None, None]:
        pipeline = self.redis_client.pipeline()
        try:
            yield self.__class__(pipeline)
        finally:
            pipeline.execute()
