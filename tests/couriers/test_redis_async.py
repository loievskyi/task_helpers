import unittest
import pickle
import uuid
import time
import threading
import datetime
import asyncio

import redis
import timeout_decorator

from task_helpers.couriers.redis_async import (
    AsyncFullQueueNameMixin,
    RedisAsyncClientTaskCourier,
    RedisAsyncWorkerTaskCourier,
    RedisAsyncClientWorkerTaskCourier,
)
from task_helpers import exceptions
from ..mixins import RedisSetupMixin


class TimeoutTestException(TimeoutError):
    pass


class AsyncFullQueueNameMixinTestCase(unittest.IsolatedAsyncioTestCase):
    """
    Tests to make sure that _get_full_queue_name is calculating correctly.
    """

    def setUp(self):
        self.mixin = AsyncFullQueueNameMixin()

    async def test_get_full_queue_name_with_prefix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = await self.mixin._get_full_queue_name(
            queue_name="test_queue_name")
        self.assertEqual(name, "test_prefix:test_queue_name")

    async def test_get_full_queue_name_with_sufix(self):
        self.mixin.prefix_queue = ""
        name = await self.mixin._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_queue_name:pending")

    async def test_get_full_queue_name_with_prefix_and_sufix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = await self.mixin._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_prefix:test_queue_name:pending")

    async def test_get_full_queue_name_without_prefix_sufix(self):
        self.mixin.prefix_queue = ""
        name = await self.mixin._get_full_queue_name("test_queue_name")
        self.assertEqual(name, "test_queue_name")


def test_func(text):
    return f"{text}{text}"


async def async_test_func(text):
    return f"{text}{text}"


class RedisAsyncClientTaskCourierTestCase(
        RedisSetupMixin, unittest.IsolatedAsyncioTestCase):
    """
    Tests to make sure that RedisAsyncClientTaskCourier is working correctly.
    """

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.async_task_courier = RedisAsyncClientTaskCourier(
            aioredis_connection=self.aioredis_connection,
            prefix_queue="tests")

    async def test___init__(self):
        courier = RedisAsyncClientTaskCourier(
            self.async_task_courier.aioredis_connection,
            test_variable="test_variable_data")
        self.assertEqual(courier.aioredis_connection,
                         self.async_task_courier.aioredis_connection)
        self.assertEqual(courier.test_variable, "test_variable_data")

    async def test__generate_task_id(self):
        self.assertFalse(hasattr(self.async_task_courier, "_uuid1_is_safe"))
        task_id = await self.async_task_courier._generate_task_id()
        self.assertTrue(hasattr(self.async_task_courier, "_uuid1_is_safe"))
        uuid1_is_safe = uuid.uuid1().is_safe is uuid.SafeUUID.safe
        expected_version = 1 if uuid1_is_safe else 4
        self.assertEqual(expected_version, task_id.version)

    async def test_add_task_to_queue_as_dict(self):
        start_task_data = {
            "test_key": "test_value",
            "int": 123,
        }
        start_task_id = await self.async_task_courier.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending"
            )
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertDictEqual(start_task_data, task_data)

    async def test_add_task_to_queue_as_sync_func(self):
        start_task_data = test_func
        start_task_id = await self.async_task_courier.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertEqual(start_task_data, task_data)
        self.assertEqual(task_data("123"), "123123")

    async def test_add_task_to_queue_as_async_func(self):
        start_task_data = async_test_func
        start_task_id = await self.async_task_courier.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertEqual(start_task_data, task_data)
        self.assertEqual(await task_data("123"), "123123")

    async def test_add_task_to_queue_is_FIFO(self):
        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )
        self.assertIsNone(task)  # queue is empty

        async def add_100_to_queue():
            return [await self.async_task_courier.add_task_to_queue(
                queue_name="test_queue_name",
                task_data=num) for num in range(100)
            ]

        start_task_ids = await add_100_to_queue()
        for num in range(100):
            task = self.redis_connection.lpop(
                await self.async_task_courier._get_full_queue_name(
                    queue_name="test_queue_name", sufix="pending")
            )
            self.assertIsNotNone(task)
            task_id, task_data = pickle.loads(task)

            self.assertEqual(num, task_data)
            self.assertEqual(start_task_ids[num], task_id)

        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )
        self.assertIsNone(task)  # queue is empty

    async def test_bulk_add_tasks_to_queue_is_FIFO(self):
        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )
        self.assertIsNone(task)  # queue is empty

        start_tasks_data = [num for num in range(100)]
        start_task_ids = await self.async_task_courier.bulk_add_tasks_to_queue(
            queue_name="test_queue_name",
            tasks_data=start_tasks_data)

        for num in range(100):
            task = self.redis_connection.lpop(
                await self.async_task_courier._get_full_queue_name(
                    queue_name="test_queue_name", sufix="pending")
            )
            self.assertIsNotNone(task)
            task_id, task_data = pickle.loads(task)

            self.assertEqual(num, task_data)
            self.assertEqual(start_task_ids[num], task_id)
            self.assertEqual(start_tasks_data[num], task_data)

        task = self.redis_connection.lpop(
            await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )
        self.assertIsNone(task)  # queue is empty

    async def test_get_task_result_if_delete_data_True(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name",
                sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        after_task_result = await self.async_task_courier.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)
        redis_task_data = self.redis_connection.lpop(key_name)

        self.assertEqual(before_task_result, after_task_result)
        self.assertIsNone(redis_task_data)

    async def test_get_task_result_if_delete_data_False(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        after_task_result = await self.async_task_courier.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=False)
        raw_task_data = self.redis_connection.lpop(key_name)
        after_task_data = pickle.loads(raw_task_data)

        self.assertEqual(before_task_result, after_task_result)
        self.assertEqual(after_task_data, before_task_result)

    async def test_get_task_result_if_result_doesnt_exists(self):
        task_id = uuid.uuid1()

        with self.assertRaises(exceptions.TaskResultDoesNotExist):
            await self.async_task_courier.get_task_result(
                queue_name="test_queue_name",
                task_id=task_id)

    async def test_get_task_result_if_result_is_PerformTaskError(self):
        before_task_id = uuid.uuid1()
        before_task_result = exceptions.PerformTaskError(
            task=(before_task_id, "test_data"),
            exception=Exception(),
            error_data="ERROR TEXT")
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        after_task_result = await self.async_task_courier.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id)
        self.assertEqual(type(after_task_result), exceptions.PerformTaskError)
        self.assertEqual(type(after_task_result.exception), Exception)
        self.assertEqual(after_task_result.error_data, "ERROR TEXT")
        self.assertEqual(after_task_result.task[0], before_task_id)
        self.assertEqual(after_task_result.task[1], "test_data")

    async def test_wait_for_task_result_if_delete_data_True(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name",
                sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        after_task_result = await self.async_task_courier.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)
        redis_task_data = self.redis_connection.lpop(key_name)

        self.assertEqual(before_task_result, after_task_result)
        self.assertIsNone(redis_task_data)

    async def test_wait_for_task_result_if_delete_data_False(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        after_task_result = await self.async_task_courier.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=False)
        raw_task_data = self.redis_connection.lpop(key_name)
        after_task_data = pickle.loads(raw_task_data)

        self.assertEqual(before_task_result, after_task_result)
        self.assertEqual(after_task_data, before_task_result)

    async def test_wait_for_task_result_if_timeout_type_int(self):
        before_task_id = uuid.uuid1()
        with self.assertRaises(TimeoutError):
            await self.async_task_courier.wait_for_task_result(
                queue_name="test_queue_name",
                task_id=before_task_id,
                timeout=1)

    async def test_wait_for_task_result_if_timeout_type_timedelta(self):
        before_task_id = uuid.uuid1()
        with self.assertRaises(TimeoutError):
            await self.async_task_courier.wait_for_task_result(
                queue_name="test_queue_name",
                task_id=before_task_id,
                timeout=datetime.timedelta(seconds=1))

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_wait_for_task_result_if_timeout_is_None(self):
        before_task_id = uuid.uuid1()
        supposed_exceptions = (
            TimeoutTestException, redis.exceptions.TimeoutError)
        with self.assertRaises(supposed_exceptions) as context:
            asyncio.run(
                self.async_task_courier.wait_for_task_result(
                    queue_name="test_queue_name",
                    task_id=before_task_id,
                    timeout=None)
            )
        self.assertNotEqual(type(context.exception), TimeoutError)

    async def test_wait_for_task_result_wait_result(self):
        def set_result_to_redis(redis_connection, key, value, sleep_time):
            time.sleep(sleep_time)
            redis_connection.rpush(key, value)

        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()

        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        thread = threading.Thread(target=set_result_to_redis, kwargs={
            "redis_connection": self.redis_connection,
            "key": key_name,
            "value": value,
            "sleep_time": 1,
        })
        thread.start()

        after_task_result = await self.async_task_courier.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)
        self.assertEqual(before_task_result, after_task_result)

    async def test_check_for_done_if_not_done(self):
        before_task_id = uuid.uuid1()
        done_status = await self.async_task_courier.check_for_done(
            queue_name="test_queue_name",
            task_id=before_task_id)
        self.assertFalse(done_status)

    async def check_and_get_result(self, queue_name, task_id):
        done_status = await self.async_task_courier.check_for_done(
            queue_name="test_queue_name",
            task_id=task_id)
        after_task_result = await self.async_task_courier.get_task_result(
            queue_name="test_queue_name",
            task_id=task_id)
        return done_status, after_task_result

    async def test_check_for_done_if_done_successfully(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)
        done_status, after_task_result = await self.check_and_get_result(
            queue_name="test_queue_name",
            task_id=before_task_id)
        self.assertTrue(done_status)
        self.assertEqual(after_task_result, before_task_result)

    async def test_check_for_done_if_done_with_error(self):
        before_task_id = uuid.uuid1()
        before_task_result = exceptions.PerformTaskError(
            task=(before_task_id, "test_data"),
            exception=Exception())
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)
        done_status, after_task_result = await self.check_and_get_result(
            queue_name="test_queue_name",
            task_id=before_task_id)
        self.assertTrue(done_status)
        self.assertEqual(type(after_task_result), exceptions.PerformTaskError)
        self.assertEqual(after_task_result.task[0], before_task_id)
        self.assertEqual(after_task_result.task[1], "test_data")

    class ClassWithRequiredInitArgs:
        def __init__(self, arg1, *, kwarg1):
            self.arg1 = arg1
            self.kwarg1 = kwarg1

    async def test_result_as_class_with_required_init_args(self):
        before_task_id = uuid.uuid1()
        before_task_result = self.ClassWithRequiredInitArgs("1", kwarg1="text")
        key_name = await self.async_task_courier._get_full_queue_name(
                queue_name="test_queue_name",
                sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.rpush(key_name, value)

        result = await self.async_task_courier.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id)
        self.assertEqual(type(result), self.ClassWithRequiredInitArgs)
        self.assertEqual(result.arg1, "1")
        self.assertEqual(result.kwarg1, "text")


class RedisAsyncWorkerTaskCourierTestCase(
        RedisSetupMixin, unittest.IsolatedAsyncioTestCase):
    """
    Tests to make sure that RedisAsyncWorkerTaskCourier is working correctly.
    """

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.async_task_courier = RedisAsyncWorkerTaskCourier(
            aioredis_connection=self.aioredis_connection,
            prefix_queue="tests")

    async def test___init__(self):
        courier = RedisAsyncWorkerTaskCourier(
            self.async_task_courier.aioredis_connection,
            test_variable="test_variable_data")
        self.assertEqual(courier.aioredis_connection,
                         self.async_task_courier.aioredis_connection)
        self.assertEqual(courier.test_variable, "test_variable_data")

    async def test_return_task_result(self):
        queue_name = "test_queue"
        task_id = uuid.uuid1()
        task_result = "test_data_test_return_task_result"
        self.async_task_courier.result_timeout = 1

        await self.async_task_courier.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_result=task_result)

        name = await self.async_task_courier._get_full_queue_name(
            queue_name=queue_name, sufix="results:") + str(task_id)
        value = pickle.loads(self.redis_connection.lpop(name))
        self.assertEqual(value, task_result)
        await asyncio.sleep(2)
        value = self.redis_connection.lpop(name)
        self.assertIsNone(value)

    async def test_bulk_return_tasks_results(self):
        queue_name = "test_queue"

        start_tasks_results = list()
        for num in range(100):
            task_id = uuid.uuid1()
            task_result = num
            start_tasks_results.append((task_id, task_result))

        self.async_task_courier.result_timeout = 100
        await self.async_task_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=start_tasks_results
        )

        for task_id, task_result in start_tasks_results:
            name = await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="results:") + str(task_id)
            value = pickle.loads(self.redis_connection.lpop(name))
            self.assertEqual(value, task_result)

    async def test_bulk_return_tasks_results_correct_timeout(self):
        queue_name = "test_queue"

        start_tasks_results = list()
        for num in range(100):
            task_id = uuid.uuid1()
            task_result = num
            start_tasks_results.append((task_id, task_result))

        self.async_task_courier.result_timeout = 2
        await self.async_task_courier.bulk_return_tasks_results(
            queue_name=queue_name,
            tasks=start_tasks_results
        )

        for task_id, task_result in start_tasks_results:
            name = await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="results:") + str(task_id)
            value = pickle.loads(self.redis_connection.lpop(name))
            self.assertEqual(value, task_result)

        await asyncio.sleep(2)
        for task_id, task_result in start_tasks_results:
            name = await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="results:") + str(task_id)
            value = self.redis_connection.lpop(name)
            self.assertIsNone(value, task_result)

    async def test_wait_for_task(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_wait_for_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="pending"), task)
        after_task_id, after_task_data = \
            await self.async_task_courier.wait_for_task(queue_name=queue_name)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_wait_for_task_if_timeout_is_None(self):
        queue_name = "test_queue_name"
        supposed_exceptions = (
            TimeoutTestException, redis.exceptions.TimeoutError)
        with self.assertRaises(supposed_exceptions) as context:
            asyncio.run(
                self.async_task_courier.wait_for_task(
                    queue_name=queue_name,
                    timeout=None)
            )
        self.assertNotEqual(type(context.exception), TimeoutError)

    async def test_wait_for_task_if_timeout(self):
        queue_name = "test_queue_name"
        with self.assertRaises(TimeoutError):
            await self.async_task_courier.wait_for_task(
                queue_name=queue_name,
                timeout=1)

    async def test_wait_for_task_wait_task(self):
        def set_task_to_redis(redis_connection, key, value, sleep_time):
            time.sleep(sleep_time)
            redis_connection.rpush(key, value)

        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_wait_for_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name=queue_name, sufix="pending")
        value = task

        thread = threading.Thread(target=set_task_to_redis, kwargs={
            "redis_connection": self.redis_connection,
            "key": key_name,
            "value": value,
            "sleep_time": 1,
        })
        thread.start()

        after_task_id, after_task_data = \
            await self.async_task_courier.wait_for_task(
                queue_name=queue_name, timeout=None)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    async def test_bulk_wait_for_tasks_if_tasks_exists(self):
        queue_name = "test_queue_name"
        key_name = await self.async_task_courier._get_full_queue_name(
            queue_name=queue_name, sufix="pending")

        before_tasks = []
        for num in range(10):
            before_task_id = uuid.uuid1()
            before_task_data = f"task_data_{num}"
            task = (before_task_id, before_task_data)
            self.redis_connection.rpush(key_name, pickle.dumps(task))
            before_tasks.append(task)

        after_tasks = await self.async_task_courier.bulk_wait_for_tasks(
            queue_name=queue_name, max_count=100)
        self.assertEqual(len(after_tasks), 10)
        self.assertListEqual(before_tasks, after_tasks)

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_bulk_wait_for_tasks_if_no_tasks(self):
        expected_exceptions = (
            TimeoutTestException, redis.exceptions.TimeoutError)
        with self.assertRaises(expected_exceptions) as context:
            asyncio.run(
                self.async_task_courier.bulk_wait_for_tasks(
                    queue_name="test_queue_name", max_count=100)
            )
        self.assertNotEqual(type(context.exception), TimeoutError)

    async def test_get_task_if_task_exists(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_get_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="pending"),
            task)
        after_task_id, after_task_data = \
            await self.async_task_courier.get_task(queue_name=queue_name)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    async def test_get_task_if_task_doesnt_exists(self):
        queue_name = "test_queue_name"
        with self.assertRaises(exceptions.TaskDoesNotExist):
            after_task_id, after_task_data = \
                await self.async_task_courier.get_task(queue_name=queue_name)

    async def test_get_task_is_FIFO(self):
        queue_name = "test_queue_name"
        before_tasks = list()

        async def check_20_results(queue_name, before_tasks):
            for num in range(20):
                after_tasks = \
                    await self.async_task_courier.get_task(queue_name)
                after_task_id, after_task_data = after_tasks
                before_task_id, before_task_data = before_tasks[num]
                self.assertEqual(before_task_id, after_task_id)
                self.assertEqual(before_task_data, after_task_data)

        for num in range(50):
            task_id = uuid.uuid1()
            task_data = f"test_get_task_data_{num}"
            task = (task_id, task_data)
            before_tasks.append(task)
            task = pickle.dumps(task)
            self.redis_connection.rpush(
                await self.async_task_courier._get_full_queue_name(
                    queue_name=queue_name, sufix="pending"),
                task
            )
        await check_20_results(queue_name, before_tasks)

    async def test_bulk_get_tasks(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_bulk_get_tasks_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            await self.async_task_courier._get_full_queue_name(
                queue_name=queue_name, sufix="pending"), task)
        tasks = await self.async_task_courier.bulk_get_tasks(
            queue_name=queue_name, max_count=20)
        after_task_id, after_task_data = tasks[0]

        self.assertEqual(type(tasks), list)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    async def test_bulk_get_tasks_if_no_tasks(self):
        queue_name = "test_queue_name"
        tasks = await self.async_task_courier.bulk_get_tasks(
            queue_name=queue_name, max_count=20)
        self.assertEqual(type(tasks), list)
        self.assertEqual(len(tasks), 0)

    async def test_bulk_get_tasks_if_many_tasks_and_FIFO(self):
        queue_name = "test_queue_name"
        before_tasks = list()

        for num in range(50):
            task_id = uuid.uuid1()
            task_data = f"test_bulk_get_tasks_data_{num}"
            task = (task_id, task_data)
            before_tasks.append(task)
            task = pickle.dumps(task)
            self.redis_connection.rpush(
                await self.async_task_courier._get_full_queue_name(
                    queue_name=queue_name, sufix="pending"), task)

        after_tasks = await self.async_task_courier.bulk_get_tasks(
            queue_name=queue_name, max_count=20)

        self.assertEqual(type(after_tasks), list)
        self.assertEqual(len(after_tasks), 20)

        for num, after_task in enumerate(after_tasks, start=0):
            after_task_id, after_task_data = after_task
            before_task_id, before_task_data = before_tasks[num]
            self.assertEqual(before_task_id, after_task_id)
            self.assertEqual(before_task_data, after_task_data)


class RedisAsyncClientWorkerTaskCourierTestCase(
        RedisAsyncClientTaskCourierTestCase,
        RedisAsyncWorkerTaskCourierTestCase,
        unittest.IsolatedAsyncioTestCase):
    """
    Tests to make sure that RedisAsyncClientWorkerTaskCourier
    is working correctly.
    """

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.async_task_courier = RedisAsyncClientWorkerTaskCourier(
            aioredis_connection=self.aioredis_connection,
            prefix_queue="tests")

    async def test___init__(self):
        courier = RedisAsyncClientWorkerTaskCourier(
            aioredis_connection=self.async_task_courier.aioredis_connection,
            test_variable="test_variable_data")
        self.assertEqual(courier.aioredis_connection,
                         self.async_task_courier.aioredis_connection)
        self.assertEqual(courier.test_variable, "test_variable_data")
