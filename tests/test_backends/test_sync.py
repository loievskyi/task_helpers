import time

import pytest

from .conftest import backend
from task_helpers.backends.sync import Backend
from task_helpers.exceptions import DoesNotExistError


class TestBackend:
    def test_get_set(self, backend: Backend):
        """Test basic get and set operations"""
        key = "test_key"
        value = b"test_value"

        backend.set(key, value)
        assert backend.get(key) == value

    def test_get_nonexistent(self, backend: Backend):
        """Test getting a nonexistent key raises DoesNotExistError"""
        with pytest.raises(DoesNotExistError):
            backend.get("nonexistent")

    def test_add_to_queue_pop_from_queue(self, backend: Backend):
        """Test adding and popping items from a queue"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_from_queue(queue_name)
        assert result == data

    def test_pop_from_empty_queue(self, backend: Backend):
        """Test popping from an empty queue raises DoesNotExistError"""
        with pytest.raises(DoesNotExistError):
            backend.pop_from_queue("empty_queue")

    def test_pop_from_empty_queue_custom_error(self, backend: Backend):
        """Test popping from empty queue with custom error class"""
        class CustomError(DoesNotExistError):
            pass

        with pytest.raises(CustomError):
            backend.pop_from_queue("empty_queue", error_class=CustomError)

    def test_bulk_add_to_queue(self, backend: Backend):
        """Test bulk adding and popping multiple items from the queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]

        backend.bulk_add_to_queue(queue_name, data)
        results = backend.bulk_pop_from_queue(queue_name, len(data))
        assert results == data

    def test_pop_from_queue_blocking_when_result_exists(self, backend: Backend):
        """Test blocking pop operation with timeout when data exists"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_from_queue_blocking(queue_name, timeout_seconds=1)
        assert result == data

    def test_pop_from_empty_queue_blocking(self, backend: Backend):
        """Test blocking pop operation with timeout from an empty queue"""
        with pytest.raises(TimeoutError):
            backend.pop_from_queue_blocking("queue_name", timeout_seconds=1)

    def test_bulk_pop_partial_items(self, backend: Backend):
        """Test getting part of items from a non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]
        backend.bulk_add_to_queue(queue_name, data)

        results = backend.bulk_pop_from_queue(queue_name, 2)
        assert results == [b"data1", b"data2"]

    def test_bulk_pop_all_remaining_items(self, backend: Backend):
        """Test getting all items with max_count larger than queue size"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        backend.bulk_add_to_queue(queue_name, data)

        results = backend.bulk_pop_from_queue(queue_name, 50)
        assert results == [b"data1", b"data2"]

    def test_bulk_pop_zero_items(self, backend: Backend):
        """Test requesting zero items from non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        backend.bulk_add_to_queue(queue_name, data)

        results = backend.bulk_pop_from_queue(queue_name, 0)
        assert results == []

    def test_bulk_pop_from_empty_queue(self, backend: Backend):
        """Test popping from an empty queue returns an empty list"""
        queue_name = "test_queue"
        results = backend.bulk_pop_from_queue(queue_name, 5)
        assert results == []

    def test_move_between_queues(self, backend: Backend):
        """Test moving items between queues and verify data location"""
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        backend.add_to_queue(source_queue, data)
        result = backend.move_between_queues(source_queue, target_queue)
        assert result == data

        # Verify data was actually moved
        with pytest.raises(DoesNotExistError):
            backend.pop_from_queue(source_queue)
        assert backend.pop_from_queue(target_queue) == data

    def test_move_between_queues_default_error(self, backend: Backend):
        """Test moving item from empty queue with default exception"""
        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(DoesNotExistError):
            backend.move_between_queues(source_queue, target_queue)

    def test_move_between_queues_custom_error(self, backend: Backend):
        """Test moving item from empty queue with custom exception"""
        class CustomError(DoesNotExistError):
            pass

        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(CustomError):
            backend.move_between_queues(source_queue, target_queue, error_class=CustomError)

    def test_move_between_queues_blocking(self, backend: Backend):
        """Test blocking move operation with timeout and data verification"""
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        backend.add_to_queue(source_queue, data)
        result = backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)
        assert result == data

        assert backend.pop_from_queue(target_queue) == data

    def test_move_between_queues_blocking_timeout_error(self, backend: Backend):
        """Test timeout while moving from an empty queue"""
        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(TimeoutError):
            backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)

    def test_pop_or_requeue_with_delete(self, backend: Backend):
        """Test pop_or_requeue with a deletion option enabled"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_or_requeue(queue_name, delete_data=True)
        assert result == data

        with pytest.raises(DoesNotExistError):
            backend.pop_from_queue(queue_name)

    def test_pop_or_requeue_without_delete(self, backend: Backend):
        """Test pop_or_requeue with a deletion option disabled"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_or_requeue(queue_name, delete_data=False)
        assert result == data

        assert backend.pop_from_queue(queue_name) == data

    def test_pop_or_requeue_blocking_with_delete(self, backend: Backend):
        """Test blocking pop_or_requeue with deletion enabled"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_or_requeue_blocking(queue_name, delete_data=True, timeout_seconds=1)
        assert result == data

        with pytest.raises(TimeoutError):
            backend.pop_or_requeue_blocking(queue_name, timeout_seconds=1)

    def test_pop_or_requeue_blocking_without_delete(self, backend: Backend):
        """Test blocking pop_or_requeue with deletion disabled"""
        queue_name = "test_queue"
        data = b"test_data"

        backend.add_to_queue(queue_name, data)
        result = backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result == data

        result2 = backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result2 == data

    def test_exists(self, backend: Backend):
        """Test exists method for checking key presence"""
        key = "test_key"
        backend.set(key, b"test_value")

        assert backend.exists(key) is True
        assert backend.exists("nonexistent") is False

    def test_expire(self, backend: Backend):
        """Test key expiration functionality"""
        key = "test_key"
        backend.set(key, b"test_value")
        backend.expire(key, 1)

        assert backend.exists(key) is True
        time.sleep(1.1)  # Wait slightly more than a second
        assert backend.exists(key) is False

    def test_expire_zero_seconds(self, backend: Backend):
        """Test expire with zero seconds for immediate deletion"""
        key = "test_key"
        backend.set(key, b"test_value")
        backend.expire(key, 0)

        assert backend.exists(key) is False

    def test_expire_negative_seconds(self, backend: Backend):
        """Test expire with negative seconds for immediate deletion"""
        key = "test_key"
        backend.set(key, b"test_value")
        backend.expire(key, -1)

        assert backend.exists(key) is False

    def test_pipeline(self, backend: Backend):
        """Test atomic execution of commands in a pipeline"""
        key1, key2 = "key1", "key2"
        value1, value2 = b"value1", b"value2"

        with backend.pipeline() as pipe:
            pipe.set(key1, value1)
            pipe.set(key2, value2)
            with pytest.raises(DoesNotExistError):
                backend.get(key1)  # Values are not set until a pipeline is executed

        assert backend.get(key1) == value1
        assert backend.get(key2) == value2
