import os
import unittest
import pickle
import uuid
import time
import threading

import redis
import timeout_decorator

from task_helper.redis import (
    FullQueueNameMixin,
    RedisClientTaskHelper,
    RedisWorkerTaskHelper,
    RedisClientWorkerTaskHelper,
)
from task_helper import exceptions


class FullQueueNameMixinTestCase(unittest.TestCase):
    """
    Tests to make sure that _get_full_queue_name is calculating correctly.
    """

    def setUp(self):
        self.mixin = FullQueueNameMixin()

    def test_get_full_queue_name_with_prefix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = self.mixin._get_full_queue_name(queue_name="test_queue_name")
        self.assertEqual(name, "test_prefix:test_queue_name")

    def test_get_full_queue_name_with_sufix(self):
        self.mixin.prefix_queue = ""
        name = self.mixin._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_queue_name:pending")

    def test_get_full_queue_name_with_prefix_and_sufix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = self.mixin._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_prefix:test_queue_name:pending")

    def test_get_full_queue_name_without_prefix_sufix(self):
        self.mixin.prefix_queue = ""
        name = self.mixin._get_full_queue_name("test_queue_name")
        self.assertEqual(name, "test_queue_name")


class RedisSetupMixin:
    """
    mixin for redis connection initializing.
    """

    def setUp(self):
        redis_host = os.environ.get("REDIS_HOST")
        redis_port = os.environ.get("REDIS_PORT")
        redis_db = os.environ.get("REDIS_DB")
        redis_password = os.environ.get("REDIS_PASSWORD", None)

        assert redis_host is not None, "redis_host is None"
        assert redis_port is not None, "redis_port is None"
        assert redis_db is not None, "redis_db is None"

        self.redis_connection = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password)
        self.redis_connection.flushdb()


def test_func(text):
    return f"{text}{text}"


class RedisClientTaskHelperTestCase(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that RedisClientTaskHelper is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.task_helper = RedisClientTaskHelper(
            redis_connection=self.redis_connection)

    class TimeoutTestException(TimeoutError):
        pass

    def test_add_task_to_queue_as_dict(self):
        start_task_data = {
            "test_key": "test_value",
            "int": 123,
        }
        start_task_id = self.task_helper.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            self.task_helper._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertDictEqual(start_task_data, task_data)

    def test_add_task_to_queue_as_func(self):
        start_task_data = test_func
        start_task_id = self.task_helper.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            self.task_helper._get_full_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertEqual(start_task_data, task_data)
        self.assertEqual(task_data("123"), "123123")

    def test_get_task_result_if_delete_data_True(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = self.task_helper._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.set(name=key_name, value=value)

        after_task_result = self.task_helper.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)
        redis_task_data = self.redis_connection.get(name=key_name)

        self.assertEqual(before_task_result, after_task_result)
        self.assertIsNone(redis_task_data)

    def test_get_task_result_if_delete_data_False(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = self.task_helper._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.set(name=key_name, value=value)

        after_task_result = self.task_helper.get_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=False)
        raw_task_data = self.redis_connection.get(name=key_name)
        after_task_data = pickle.loads(raw_task_data)

        self.assertEqual(before_task_result, after_task_result)
        self.assertEqual(after_task_data, before_task_result)

    def test_get_task_result_if_result_doesnt_exists(self):
        task_id = uuid.uuid1()

        with self.assertRaises(exceptions.TaskResultDoesNotExist):
            self.task_helper.get_task_result(
                queue_name="test_queue_name",
                task_id=task_id)

    def test_wait_for_task_result_if_delete_data_True(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = self.task_helper._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.set(name=key_name, value=value)

        after_task_result = self.task_helper.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)
        redis_task_data = self.redis_connection.get(name=key_name)

        self.assertEqual(before_task_result, after_task_result)
        self.assertIsNone(redis_task_data)

    def test_wait_for_task_result_if_delete_data_False(self):
        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()
        key_name = self.task_helper._get_full_queue_name(
            queue_name="test_queue_name",
            sufix="results:") + str(before_task_id)
        value = pickle.dumps(before_task_result)
        self.redis_connection.set(name=key_name, value=value)

        after_task_result = self.task_helper.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=False)
        raw_task_data = self.redis_connection.get(name=key_name)
        after_task_data = pickle.loads(raw_task_data)

        self.assertEqual(before_task_result, after_task_result)
        self.assertEqual(after_task_data, before_task_result)

    def test_wait_for_task_result_if_timeout(self):
        before_task_id = uuid.uuid1()
        with self.assertRaises(TimeoutError):
            self.task_helper.wait_for_task_result(
                queue_name="test_queue_name",
                task_id=before_task_id,
                timeout=1)

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_wait_for_task_result_if_timeout_is_None(self):
        before_task_id = uuid.uuid1()
        supposed_exceptions = (
            self.TimeoutTestException, redis.exceptions.TimeoutError)
        with self.assertRaises(supposed_exceptions) as context:
            self.task_helper.wait_for_task_result(
                queue_name="test_queue_name",
                task_id=before_task_id,
                timeout=None)
        self.assertNotEqual(type(context.exception), TimeoutError)

    def test_wait_for_task_result_wait_result(self):
        def set_result_to_redis(redis_connection, key, value, sleep_time):
            time.sleep(sleep_time)
            redis_connection.set(key, value)

        before_task_result = "test_result_123"
        before_task_id = uuid.uuid1()

        key_name = self.task_helper._get_full_queue_name(
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

        after_task_result = self.task_helper.wait_for_task_result(
            queue_name="test_queue_name",
            task_id=before_task_id,
            delete_data=True)

        self.assertEqual(before_task_result, after_task_result)


class RedisWorkerTaskHelperTestCase(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that RedisWorkerTaskHelper is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.task_helper = RedisWorkerTaskHelper(
            redis_connection=self.redis_connection)

    class TimeoutTestException(TimeoutError):
        pass

    def test_return_task_result(self):
        queue_name = "test_queue"
        task_id = uuid.uuid1()
        task_data = "test_data_test_return_task_result"
        self.task_helper.result_timeout = 1

        self.task_helper.return_task_result(
            queue_name=queue_name,
            task_id=task_id,
            task_data=task_data)

        name = self.task_helper._get_full_queue_name(
            queue_name=queue_name, sufix="results:") + str(task_id)
        value = pickle.loads(self.redis_connection.get(name))
        self.assertEqual(value, task_data)
        time.sleep(2)
        value = self.redis_connection.get(name)
        self.assertIsNone(value)

    def test_wait_for_task(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_wait_for_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            self.task_helper._get_full_queue_name(
                queue_name=queue_name, sufix="pending"), task)
        after_task_id, after_task_data = self.task_helper.wait_for_task(
            queue_name=queue_name)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_wait_for_task_if_timeout_is_None(self):
        queue_name = "test_queue_name"
        supposed_exceptions = (
            self.TimeoutTestException, redis.exceptions.TimeoutError)
        with self.assertRaises(supposed_exceptions) as context:
            self.task_helper.wait_for_task(
                queue_name=queue_name,
                timeout=None)
        self.assertNotEqual(type(context.exception), TimeoutError)

    def test_wait_for_task_if_timeout(self):
        queue_name = "test_queue_name"
        with self.assertRaises(TimeoutError):
            self.task_helper.wait_for_task(
                queue_name=queue_name,
                timeout=1)

    def test_wait_for_task_wait_task(self):
        def set_task_to_redis(redis_connection, key, value, sleep_time):
            time.sleep(sleep_time)
            redis_connection.rpush(key, value)

        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_wait_for_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        key_name = self.task_helper._get_full_queue_name(
            queue_name=queue_name, sufix="pending")
        value = task

        thread = threading.Thread(target=set_task_to_redis, kwargs={
            "redis_connection": self.redis_connection,
            "key": key_name,
            "value": value,
            "sleep_time": 1,
        })
        thread.start()

        after_task_id, after_task_data = self.task_helper.wait_for_task(
            queue_name=queue_name, timeout=None)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    def test_get_task_if_task_exists(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_get_task_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            self.task_helper._get_full_queue_name(
                queue_name=queue_name, sufix="pending"), task)
        after_task_id, after_task_data = self.task_helper.get_task(
            queue_name=queue_name)

        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    def test_get_task_if_task_doesnt_exists(self):
        queue_name = "test_queue_name"
        with self.assertRaises(exceptions.TaskDoesNotExist):
            after_task_id, after_task_data = self.task_helper.get_task(
                queue_name=queue_name)

    def test_get_task_is_FIFO(self):
        queue_name = "test_queue_name"
        before_tasks = list()

        for num in range(50):
            task_id = uuid.uuid1()
            task_data = f"test_get_task_data_{num}"
            task = (task_id, task_data)
            before_tasks.append(task)
            task = pickle.dumps(task)
            self.redis_connection.rpush(
                self.task_helper._get_full_queue_name(
                    queue_name=queue_name, sufix="pending"), task)

        for num in range(20):
            after_tasks = self.task_helper.get_task(queue_name)
            after_task_id, after_task_data = after_tasks
            before_task_id, before_task_data = before_tasks[num]
            self.assertEqual(before_task_id, after_task_id)
            self.assertEqual(before_task_data, after_task_data)

    def test_get_tasks(self):
        queue_name = "test_queue_name"
        before_task_id = uuid.uuid1()
        before_task_data = "test_get_tasks_data"
        task = pickle.dumps((before_task_id, before_task_data))

        self.redis_connection.rpush(
            self.task_helper._get_full_queue_name(
                queue_name=queue_name, sufix="pending"), task)
        tasks = self.task_helper.get_tasks(
            queue_name=queue_name, max_count=20)
        after_task_id, after_task_data = tasks[0]

        self.assertEqual(type(tasks), list)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(before_task_id, after_task_id)
        self.assertEqual(before_task_data, after_task_data)

    def test_get_tasks_if_no_tasks(self):
        queue_name = "test_queue_name"
        tasks = self.task_helper.get_tasks(
            queue_name=queue_name, max_count=20)
        self.assertEqual(type(tasks), list)
        self.assertEqual(len(tasks), 0)

    def test_get_tasks_if_many_tasks_and_FIFO(self):
        queue_name = "test_queue_name"
        before_tasks = list()

        for num in range(50):
            task_id = uuid.uuid1()
            task_data = f"test_get_tasks_data_{num}"
            task = (task_id, task_data)
            before_tasks.append(task)
            task = pickle.dumps(task)
            self.redis_connection.rpush(
                self.task_helper._get_full_queue_name(
                    queue_name=queue_name, sufix="pending"), task)

        after_tasks = self.task_helper.get_tasks(
            queue_name=queue_name, max_count=20)

        self.assertEqual(type(after_tasks), list)
        self.assertEqual(len(after_tasks), 20)

        for num, after_task in enumerate(after_tasks, start=0):
            after_task_id, after_task_data = after_task
            before_task_id, before_task_data = before_tasks[num]
            self.assertEqual(before_task_id, after_task_id)
            self.assertEqual(before_task_data, after_task_data)


class RedisClientWorkerTaskHelperTestCase(
        RedisClientTaskHelperTestCase,
        RedisWorkerTaskHelperTestCase):
    """
    Tests to make sure that RedisClientWorkerTaskHelper is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.task_helper = RedisClientWorkerTaskHelper(
            redis_connection=self.redis_connection)


if __name__ == "__main__":
    unittest.main()
