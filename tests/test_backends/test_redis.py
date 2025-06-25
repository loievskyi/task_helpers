import time

import pytest
import redis

from task_helpers.backends.redis import RedisBackend
from task_helpers.exceptions import DoesNotExistError


@pytest.fixture
def mock_redis_client() -> redis.Redis:
    """Create a Redis client instance for testing using a separate database."""
    return redis.Redis(db=1)

@pytest.fixture
def redis_backend(mock_redis_client) -> RedisBackend:
    """Create a clean RedisBackend instance for each test.

    Flushes the database before each test to ensure isolation.
    """
    mock_redis_client.flushdb()
    return RedisBackend(mock_redis_client)


class TestRedisBackend:
    def test_get_set(self, redis_backend):
        key = "test_key"
        value = b"test_value"

        redis_backend.set(key, value)
        assert redis_backend.get(key) == value

    def test_get_nonexistent(self, redis_backend):
        with pytest.raises(DoesNotExistError):
            redis_backend.get("nonexistent")

    def test_add_to_queue_pop_from_queue(self, redis_backend):
        queue_name = "test_queue"
        data = b"test_data"

        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_from_queue(queue_name)
        assert result == data

    def test_pop_from_empty_queue(self, redis_backend):
        with pytest.raises(DoesNotExistError):
            redis_backend.pop_from_queue("empty_queue")

    def test_pop_from_empty_queue_custom_error(self, redis_backend):
        class CustomError(DoesNotExistError):
            pass

        with pytest.raises(CustomError):
            redis_backend.pop_from_queue("empty_queue", error_class=CustomError)

    def test_bulk_add_to_queue(self, redis_backend):
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]

        redis_backend.bulk_add_to_queue(queue_name, data)
        results = redis_backend.bulk_pop_from_queue(queue_name, len(data))
        assert results == data

    def test_pop_from_queue_blocking_when_result_exists(self, redis_backend):
        """Test blocking pop operation with timeout"""
        queue_name = "test_queue"
        data = b"test_data"

        # Test immediate return when data exists
        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_from_queue_blocking(queue_name, timeout_seconds=1)
        assert result == data

    def test_pop_from_empty_queue_blocking(self, redis_backend):
        """Test blocking pop operation with timeout"""
        with pytest.raises(TimeoutError):
            redis_backend.pop_from_queue_blocking("queue_name", timeout_seconds=1)

    def test_bulk_pop_partial_items(self, redis_backend):
        """Test getting part of items from a non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]
        redis_backend.bulk_add_to_queue(queue_name, data)

        results = redis_backend.bulk_pop_from_queue(queue_name, 2)
        assert results == [b"data1", b"data2"]

    def test_bulk_pop_all_remaining_items(self, redis_backend):
        """Test getting all items with count larger than queue size"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        redis_backend.bulk_add_to_queue(queue_name, data)

        results = redis_backend.bulk_pop_from_queue(queue_name, 50)
        assert results == [b"data1", b"data2"]

    def test_bulk_pop_zero_items(self, redis_backend):
        """Test requesting zero items from non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        redis_backend.bulk_add_to_queue(queue_name, data)

        results = redis_backend.bulk_pop_from_queue(queue_name, 0)
        assert results == []

    def test_bulk_pop_from_empty_queue(self, redis_backend):
        """Test popping from an empty queue"""
        queue_name = "test_queue"
        results = redis_backend.bulk_pop_from_queue(queue_name, 5)
        assert results == []

    def test_move_between_queues(self, redis_backend):
        # Test moving items between queues
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        redis_backend.add_to_queue(source_queue, data)
        result = redis_backend.move_between_queues(source_queue, target_queue)
        assert result == data

        # Verify data was actually moved
        with pytest.raises(DoesNotExistError):
            redis_backend.pop_from_queue(source_queue)
        assert redis_backend.pop_from_queue(target_queue) == data

    def test_move_between_queues_default_error(self, redis_backend):
        """Test moving item from empty queue with custom exception"""

        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(DoesNotExistError):
            redis_backend.move_between_queues(source_queue, target_queue)


    def test_move_between_queues_custom_error(self, redis_backend):
        """Test moving item from empty queue with custom exception"""
        class CustomError(DoesNotExistError):
            pass

        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(CustomError):
            redis_backend.move_between_queues(source_queue, target_queue, error_class=CustomError)

    def test_move_between_queues_blocking(self, redis_backend):
        """Test blocking move operation with timeout"""
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        # Test immediate move when data exists
        redis_backend.add_to_queue(source_queue, data)
        result = redis_backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)
        assert result == data

        # Verify data was moved
        assert redis_backend.pop_from_queue(target_queue) == data

    def test_move_between_queues_blocking_timeout_error(self, redis_backend):
        """Test moving item from empty queue with custom exception"""

        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(TimeoutError):
            redis_backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)


    def test_pop_or_requeue_with_delete(self, redis_backend):
        # Test pop_or_requeue with deletion
        queue_name = "test_queue"
        data = b"test_data"

        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_or_requeue(queue_name, delete_data=True)
        assert result == data

        # Verify data was deleted
        with pytest.raises(DoesNotExistError):
            redis_backend.pop_from_queue(queue_name)

    def test_pop_or_requeue_without_delete(self, redis_backend):
        # Test pop_or_requeue without deletion
        queue_name = "test_queue"
        data = b"test_data"

        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_or_requeue(queue_name, delete_data=False)
        assert result == data

        # Verify data remains in queue
        assert redis_backend.pop_from_queue(queue_name) == data

    def test_pop_or_requeue_blocking_with_delete(self, redis_backend):
        """Test blocking pop_or_requeue with deletion"""
        queue_name = "test_queue"
        data = b"test_data"

        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_or_requeue_blocking(queue_name, delete_data=True, timeout_seconds=1)
        assert result == data

        # Verify data was deleted
        with pytest.raises(TimeoutError):
            redis_backend.pop_or_requeue_blocking(queue_name, timeout_seconds=1)

    def test_pop_or_requeue_blocking_without_delete(self, redis_backend):
        """Test blocking pop_or_requeue without deletion"""
        queue_name = "test_queue"
        data = b"test_data"

        redis_backend.add_to_queue(queue_name, data)
        result = redis_backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result == data

        # Verify data remains in queue
        result2 = redis_backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result2 == data

    def test_exists(self, redis_backend):
        # Test exists method
        key = "test_key"
        redis_backend.set(key, b"test_value")

        assert redis_backend.exists(key) is True
        assert redis_backend.exists("nonexistent") is False

    def test_expire(self, redis_backend):
        # Test key expiration
        key = "test_key"
        redis_backend.set(key, b"test_value")
        redis_backend.expire(key, 1)

        assert redis_backend.exists(key) is True
        time.sleep(1.1)  # Wait slightly more than a second
        assert redis_backend.exists(key) is False

    def test_expire_zero_seconds(self, redis_backend):
        """Test expire with zero seconds should delete the key immediately"""
        key = "test_key"
        redis_backend.set(key, b"test_value")
        redis_backend.expire(key, 0)

        assert redis_backend.exists(key) is False

    def test_expire_negative_seconds(self, redis_backend):
        """Test expire with negative seconds should delete the key immediately"""
        key = "test_key"
        redis_backend.set(key, b"test_value")
        redis_backend.expire(key, -1)

        assert redis_backend.exists(key) is False

    def test_pipeline(self, redis_backend):
        """Test that a pipeline executes commands atomically"""
        key1, key2 = "key1", "key2"
        value1, value2 = b"value1", b"value2"

        with redis_backend.pipeline() as pipe:
            pipe.set(key1, value1)
            pipe.set(key2, value2)
            with pytest.raises(DoesNotExistError):
                redis_backend.get(key1)  # Values are not set until a pipeline is executed

        # After pipeline execution, values are available
        assert redis_backend.get(key1) == value1
        assert redis_backend.get(key2) == value2
