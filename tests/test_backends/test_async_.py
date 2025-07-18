import asyncio

import pytest

from tests.conftest import async_backend
from task_helpers.backends.async_ import AsyncBackend
from task_helpers.exceptions import DoesNotExistError


class TestAsyncBackend:
    @pytest.mark.asyncio
    async def test_get_set(self, async_backend: AsyncBackend):
        """Test basic get and set operations"""
        key = "test_key"
        value = b"test_value"

        await async_backend.set(key, value)
        assert await async_backend.get(key) == value

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, async_backend: AsyncBackend):
        """Test getting a nonexistent key raises DoesNotExistError"""
        with pytest.raises(DoesNotExistError):
            await async_backend.get("nonexistent")

    @pytest.mark.asyncio
    async def test_add_to_queue_pop_from_queue(self, async_backend: AsyncBackend):
        """Test adding and popping items from a queue"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_from_queue(queue_name)
        assert result == data

    @pytest.mark.asyncio
    async def test_pop_from_empty_queue(self, async_backend: AsyncBackend):
        """Test popping from an empty queue raises DoesNotExistError"""
        with pytest.raises(DoesNotExistError):
            await async_backend.pop_from_queue("empty_queue")

    @pytest.mark.asyncio
    async def test_pop_from_empty_queue_custom_error(self, async_backend: AsyncBackend):
        """Test popping from empty queue with custom error class"""
        class CustomError(DoesNotExistError):
            pass

        with pytest.raises(CustomError):
            await async_backend.pop_from_queue("empty_queue", error_class=CustomError)

    @pytest.mark.asyncio
    async def test_bulk_add_to_queue(self, async_backend: AsyncBackend):
        """Test bulk adding and popping multiple items from the queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]

        await async_backend.bulk_add_to_queue(queue_name, data)
        results = await async_backend.bulk_pop_from_queue(queue_name, len(data))
        assert results == data

    @pytest.mark.asyncio
    async def test_pop_from_queue_blocking_when_result_exists(self, async_backend: AsyncBackend):
        """Test blocking pop operation with timeout when data exists"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_from_queue_blocking(queue_name, timeout_seconds=1)
        assert result == data

    @pytest.mark.asyncio
    async def test_pop_from_empty_queue_blocking(self, async_backend: AsyncBackend):
        """Test blocking pop operation with timeout from an empty queue"""
        with pytest.raises(TimeoutError):
            await async_backend.pop_from_queue_blocking("queue_name", timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_bulk_pop_partial_items(self, async_backend: AsyncBackend):
        """Test getting part of items from a non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2", b"data3"]
        await async_backend.bulk_add_to_queue(queue_name, data)

        results = await async_backend.bulk_pop_from_queue(queue_name, 2)
        assert results == [b"data1", b"data2"]

    @pytest.mark.asyncio
    async def test_bulk_pop_all_remaining_items(self, async_backend: AsyncBackend):
        """Test getting all items with max_count larger than queue size"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        await async_backend.bulk_add_to_queue(queue_name, data)

        results = await async_backend.bulk_pop_from_queue(queue_name, 50)
        assert results == [b"data1", b"data2"]

    @pytest.mark.asyncio
    async def test_bulk_pop_zero_items(self, async_backend: AsyncBackend):
        """Test requesting zero items from non-empty queue"""
        queue_name = "test_queue"
        data = [b"data1", b"data2"]
        await async_backend.bulk_add_to_queue(queue_name, data)

        results = await async_backend.bulk_pop_from_queue(queue_name, 0)
        assert results == []

    @pytest.mark.asyncio
    async def test_bulk_pop_from_empty_queue(self, async_backend: AsyncBackend):
        """Test popping from an empty queue returns an empty list"""
        queue_name = "test_queue"
        results = await async_backend.bulk_pop_from_queue(queue_name, 5)
        assert results == []

    @pytest.mark.asyncio
    async def test_move_between_queues(self, async_backend: AsyncBackend):
        """Test moving items between queues and verify data location"""
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        await async_backend.add_to_queue(source_queue, data)
        result = await async_backend.move_between_queues(source_queue, target_queue)
        assert result == data

        with pytest.raises(DoesNotExistError):
            await async_backend.pop_from_queue(source_queue)
        assert await async_backend.pop_from_queue(target_queue) == data

    @pytest.mark.asyncio
    async def test_move_between_queues_default_error(self, async_backend: AsyncBackend):
        """Test moving item from empty queue with default exception"""
        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(DoesNotExistError):
            await async_backend.move_between_queues(source_queue, target_queue)

    @pytest.mark.asyncio
    async def test_move_between_queues_custom_error(self, async_backend: AsyncBackend):
        """Test moving item from empty queue with custom exception"""

        class CustomError(DoesNotExistError):
            pass

        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(CustomError):
            await async_backend.move_between_queues(source_queue, target_queue, error_class=CustomError)

    @pytest.mark.asyncio
    async def test_move_between_queues_blocking(self, async_backend: AsyncBackend):
        """Test blocking move operation with timeout"""
        source_queue = "source"
        target_queue = "target"
        data = b"test_data"

        await async_backend.add_to_queue(source_queue, data)
        result = await async_backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)
        assert result == data

        assert await async_backend.pop_from_queue(target_queue) == data

    @pytest.mark.asyncio
    async def test_move_between_queues_blocking_timeout_error(self, async_backend: AsyncBackend):
        """Test timeout while moving from an empty queue"""
        source_queue = "empty_source_queue"
        target_queue = "target_queue"

        with pytest.raises(TimeoutError):
            await async_backend.move_between_queues_blocking(source_queue, target_queue, timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_pop_or_requeue_with_delete(self, async_backend: AsyncBackend):
        """Test pop_or_requeue with deletion enabled"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_or_requeue(queue_name, delete_data=True)
        assert result == data

        with pytest.raises(DoesNotExistError):
            await async_backend.pop_from_queue(queue_name)

    @pytest.mark.asyncio
    async def test_pop_or_requeue_without_delete(self, async_backend: AsyncBackend):
        """Test pop_or_requeue with deletion disabled"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_or_requeue(queue_name, delete_data=False)
        assert result == data

        assert await async_backend.pop_from_queue(queue_name) == data

    @pytest.mark.asyncio
    async def test_pop_or_requeue_blocking_with_delete(self, async_backend: AsyncBackend):
        """Test blocking pop_or_requeue with deletion enabled"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_or_requeue_blocking(queue_name, delete_data=True, timeout_seconds=1)
        assert result == data

        with pytest.raises(TimeoutError):
            await async_backend.pop_or_requeue_blocking(queue_name, timeout_seconds=1)

    @pytest.mark.asyncio
    async def test_pop_or_requeue_blocking_without_delete(self, async_backend: AsyncBackend):
        """Test blocking pop_or_requeue with deletion disabled"""
        queue_name = "test_queue"
        data = b"test_data"

        await async_backend.add_to_queue(queue_name, data)
        result = await async_backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result == data

        result2 = await async_backend.pop_or_requeue_blocking(queue_name, delete_data=False, timeout_seconds=1)
        assert result2 == data

    @pytest.mark.asyncio
    async def test_exists(self, async_backend: AsyncBackend):
        """Test exists method for checking key presence"""
        key = "test_key"
        await async_backend.set(key, b"test_value")

        assert await async_backend.exists(key) is True
        assert await async_backend.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_expire(self, async_backend: AsyncBackend):
        """Test key expiration functionality"""
        key = "test_key"
        await async_backend.set(key, b"test_value")
        await async_backend.expire(key, 1)

        assert await async_backend.exists(key) is True
        await asyncio.sleep(1.1)  # Wait slightly more than a second
        assert await async_backend.exists(key) is False

    @pytest.mark.asyncio
    async def test_expire_zero_seconds(self, async_backend: AsyncBackend):
        """Test expire with zero seconds for immediate deletion"""
        key = "test_key"
        await async_backend.set(key, b"test_value")
        await async_backend.expire(key, 0)

        assert await async_backend.exists(key) is False

    @pytest.mark.asyncio
    async def test_expire_negative_seconds(self, async_backend: AsyncBackend):
        """Test expire with negative seconds for immediate deletion"""
        key = "test_key"
        await async_backend.set(key, b"test_value")
        await async_backend.expire(key, -1)

        assert await async_backend.exists(key) is False

    @pytest.mark.asyncio
    async def test_pipeline(self, async_backend: AsyncBackend):
        """Test atomic execution of commands in a pipeline"""
        key1, key2 = "key1", "key2"
        value1, value2 = b"value1", b"value2"

        async with async_backend.pipeline() as pipe:
            await pipe.set(key1, value1)
            await pipe.set(key2, value2)
            with pytest.raises(DoesNotExistError):
                await async_backend.get(key1)

        assert await async_backend.get(key1) == value1
        assert await async_backend.get(key2) == value2
