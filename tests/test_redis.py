import unittest
import redis

from task_helper.redis import (
    FullQueueNameMixin,
    RedisClientTaskHelper,
)


class TestFullQueueNameMixin(unittest.TestCase):
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

