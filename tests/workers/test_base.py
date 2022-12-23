import uuid
import unittest

import timeout_decorator

from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.workers.base import BaseWorker
from ..mixins import RedisSetupMixin


class BaseWorkerTestCadse(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that BaseClientTaskCourier is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.queue_name = "test_queue_name"
        self.task_courier = RedisClientWorkerTaskCourier(self.redis_connection)
        self.worker = BaseWorker(task_courier=self.task_courier)

        # monkey patching
        self.worker.queue_name = self.queue_name
        self.worker.max_tasks_per_iteration = 100

    class TimeoutTestException(TimeoutError):
        pass

    def test___init__(self):
        worker = BaseWorker(task_courier=self.task_courier,
                            max_tasks_per_iteration=5,
                            test_variable="test_variable_data")
        self.assertEqual(worker.task_courier, self.task_courier)
        self.assertEqual(worker.max_tasks_per_iteration, 5)
        self.assertEqual(worker.test_variable, "test_variable_data")

    def test_wait_for_tasks(self):
        before_tasks = []
        for num in range(10):
            task_data = f"task_data_{num}"
            task_id = self.task_courier.add_task_to_queue(
                queue_name=self.queue_name,
                task_data=task_data)
            before_tasks.append((task_id, task_data))

        after_tasks = self.worker.wait_for_tasks()
        self.assertEqual(len(after_tasks), 10)
        self.assertListEqual(before_tasks, after_tasks)

    @timeout_decorator.timeout(1, timeout_exception=TimeoutTestException)
    def test_wait_for_tasks_if_no_tasks(self):
        with self.assertRaises(self.TimeoutTestException) as context:
            self.worker.wait_for_tasks()
        self.assertNotEqual(type(context.exception), TimeoutError)

    def test_wait_for_tasks_if_count_of_tasks_is_greater_than_max_tasks_per_iteration(self):
        before_tasks = []
        for num in range(150):
            task_data = f"task_data_{num}"
            task_id = self.task_courier.add_task_to_queue(
                queue_name=self.queue_name,
                task_data=task_data)
            before_tasks.append((task_id, task_data))

        after_tasks = self.worker.wait_for_tasks()
        self.assertEqual(len(after_tasks), 100)
        self.assertListEqual(before_tasks[:100], after_tasks)

    def test_perform_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.perform_tasks(tasks=[(uuid.uuid1(), "task_data")])
