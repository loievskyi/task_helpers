import os
import unittest
import pickle

import redis

from task_helper.redis import (
    FullQueueNameMixin,
    RedisClientTaskHelper,
)


class TestFullQueueNameMixin(unittest.TestCase):
    """
    Tests to make sure that _get_ful_queue_name is calculating correctly.
    """

    def setUp(self):
        self.mixin = FullQueueNameMixin()

    def test_get_ful_queue_name_with_prefix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = self.mixin._get_ful_queue_name(queue_name="test_queue_name")
        self.assertEqual(name, "test_prefix:test_queue_name")

    def test_get_ful_queue_name_with_sufix(self):
        self.mixin.prefix_queue = ""
        name = self.mixin._get_ful_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_queue_name:pending")

    def test_get_ful_queue_name_with_prefix_and_sufix(self):
        self.mixin.prefix_queue = "test_prefix"
        name = self.mixin._get_ful_queue_name(
            queue_name="test_queue_name",
            sufix="pending")
        self.assertEqual(name, "test_prefix:test_queue_name:pending")

    def test_get_ful_queue_name_without_prefix_sufix(self):
        self.mixin.prefix_queue = ""
        name = self.mixin._get_ful_queue_name("test_queue_name")
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
        self.task_helper = RedisClientTaskHelper(
            redis_connection=self.redis_connection)


def test_func(text):
    return f"{text}{text}"


class TestRedisClientTaskHelper(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that RedisClientTaskHelper is working correctly.
    """

    def setUp(self):
        super().setUp()

    def test_add_task_to_queue_as_dict(self):
        start_task_data = {
            "test_key": "test_value",
            "int": 123,
        }
        start_task_id = self.task_helper.add_task_to_queue(
            queue_name="test_queue_name",
            task_data=start_task_data)

        task = self.redis_connection.lpop(
            self.task_helper._get_ful_queue_name(
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
            self.task_helper._get_ful_queue_name(
                queue_name="test_queue_name", sufix="pending")
        )

        self.assertIsNotNone(task)
        task_id, task_data = pickle.loads(task)
        self.assertEqual(start_task_id, task_id)
        self.assertEqual(start_task_data, task_data)
        self.assertEqual(task_data("123"), "123123")


if __name__ == "__main__":
    unittest.main()
