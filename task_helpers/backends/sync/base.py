from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Type, Generator

from task_helpers.exceptions import DoesNotExistError


class WriteOnlyBackend(ABC):
    def __init__(self, backend_connection, *args, **kwargs):
        """Initialize backend connection."""
        assert backend_connection is not None, "backend_connection is required"

    @abstractmethod
    def set(self, key: str, value: bytes) -> None:
        """Set value by key."""

    @abstractmethod
    def add_to_queue(self, queue_name: str, data: bytes) -> None:
        """Add single item to queue."""

    @abstractmethod
    def bulk_add_to_queue(self, queue_name: str, data: list[bytes]) -> None:
        """Add multiple items to queue."""

    @abstractmethod
    def expire(self, key: str, seconds: int) -> None:
        """Set the expiration time for a key."""

    @abstractmethod
    @contextmanager
    def pipeline(self) -> Generator["WriteOnlyBackend", None, None]:
        """Create a pipeline for batch operations."""


class Backend(WriteOnlyBackend, ABC):
    @abstractmethod
    def get(self, key: str) -> bytes:
        """Get value by key."""

    @abstractmethod
    def pop_from_queue(self, queue_name: str, error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop single item from queue."""

    @abstractmethod
    def pop_from_queue_blocking(self, queue_name: str, timeout_seconds: int = None) -> bytes:
        """Pop single item from queue with blocking."""

    @abstractmethod
    def bulk_pop_from_queue(self, queue_name: str, max_count: int) -> list[bytes]:
        """Pop multiple items from queue."""

    @abstractmethod
    def move_between_queues(self, source_queue_name: str, target_queue_name: str,
                            error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Move a single item between queues."""

    @abstractmethod
    def move_between_queues_blocking(self, source_queue_name: str, target_queue_name: str,
                                     timeout_seconds: int = None) -> bytes:
        """Move a single item between queues with blocking."""

    @abstractmethod
    def pop_or_requeue(self, queue_name: str,
                       delete_data: bool = True,
                       error_class: Type[DoesNotExistError] = DoesNotExistError) -> bytes:
        """Pop item from queue or requeue it back."""

    @abstractmethod
    def pop_or_requeue_blocking(self, queue_name: str,
                                delete_data: bool = True,
                                timeout_seconds: int = None) -> bytes:
        """Pop item from queue or requeue it back with blocking."""

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if the key exists."""
