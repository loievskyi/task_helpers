from abc import ABC, abstractmethod
from typing import Type, AsyncContextManager

from task_helpers.exceptions import DoesNotExistError


class AsyncWriteOnlyBackend(ABC):
    def __init__(self, backend_connection, *args, **kwargs):
        """Initialize backend connection."""
        assert backend_connection is not None, "backend_connection is required"

    @abstractmethod
    async def set(self, key: str, value: bytes) -> None:
        """Set value by key."""

    @abstractmethod
    async def add_to_queue(self, queue_name: str, data: bytes) -> None:
        """Add single item to queue."""

    @abstractmethod
    async def bulk_add_to_queue(self, queue_name: str, data: list[bytes]) -> None:
        """Add multiple items to queue."""

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> None:
        """Set the expiration time for a key."""

    @abstractmethod
    def pipeline(self) -> AsyncContextManager["AsyncWriteOnlyBackend"]:
        """Create a pipeline for batch operations."""


class AsyncBackend(AsyncWriteOnlyBackend, ABC):
    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Get value by key."""

    @abstractmethod
    async def pop_from_queue(self, queue_name: str, error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop single item from queue."""

    @abstractmethod
    async def pop_from_queue_blocking(self, queue_name: str, timeout_seconds: int = None) -> bytes:
        """Pop single item from queue with blocking."""

    @abstractmethod
    async def bulk_pop_from_queue(self, queue_name: str, max_count: int) -> list[bytes]:
        """Pop multiple items from queue."""

    @abstractmethod
    async def move_between_queues(self, source_queue_name: str, target_queue_name: str,
                                  error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Move a single item between queues."""

    @abstractmethod
    async def move_between_queues_blocking(self, source_queue_name: str, target_queue_name: str,
                                           timeout_seconds: int = None) -> bytes:
        """Move a single item between queues with blocking."""

    @abstractmethod
    async def pop_or_requeue(self, queue_name: str,
                             delete_data: bool = True,
                             error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop item from queue or requeue it back."""

    @abstractmethod
    async def pop_or_requeue_blocking(self, queue_name: str,
                                      delete_data: bool = True,
                                      timeout_seconds: int = None) -> bytes:
        """Pop item from queue or requeue it back with blocking."""

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if the key exists."""
