import uuid
import unittest
import threading

import timeout_decorator

from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.worker_handlers.base import BaseWorkerHandler
from task_helpers.workers.base_async import BaseAsyncWorker
from task_helpers.workers.base import BaseWorker
from task_helpers import exceptions
from ..mixins import RedisSetupMixin


class BaseWorkerHandlerTestCase(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that BaseWorker is working correctly.
    """

    class TestWorkerHandler(BaseWorkerHandler):
        worker_class = BaseWorker
        task_courier_class = RedisClientWorkerTaskCourier
        queue_name = "test_queue_name"

        def create_worker_instance(self, worker_init_kwargs):
            redis_connection = self.redis_connection
            task_courier = RedisClientWorkerTaskCourier(
                redis_connection=redis_connection)
            return self.worker_class(redis_connection=redis_connection,
                                     task_courier=task_courier,
                                     queue_name=self.queue_name,
                                     **worker_init_kwargs)

    def setUp(self):
        super().setUp()
        self.queue_name = "test_queue_name"
        self.task_courier = RedisClientWorkerTaskCourier(self.redis_connection)
        self.worker = BaseWorker(task_courier=self.task_courier)
        self.worker_handler = BaseWorkerHandler(worker_class=BaseWorker)
        self.test_worker_handler = self.TestWorkerHandler()

        # monkey patching
        self.worker.queue_name = self.queue_name
        self.worker.max_tasks_per_iteration = 100

    """
    ===========================================================================
    process_name
    ===========================================================================
    """

    def test_process_name_if_worker_setted(self):
        expected_process_name = \
            f"taskhelpers." \
            f"{self.test_worker_handler.worker_class.__name__}.None"
        self.assertEqual(
            self.test_worker_handler.process_name,
            expected_process_name)

    def test_process_name_if_worker_not_setted(self):
        worker_handler = BaseWorkerHandler()
        self.assertEqual(worker_handler.process_name, "taskhelpers.worker")

    def test_process_name_if_worker_setted_by_kwarg(self):
        class TestWorker(BaseWorker):
            queue_name = "test_queue_name"

        worker_handler = BaseWorkerHandler(worker_class=TestWorker)
        expected_process_name = \
            f"taskhelpers." \
            f"{worker_handler.worker_class.__name__}.test_queue_name"
        self.assertEqual(
            worker_handler.process_name,
            expected_process_name)

    """
    ===========================================================================
    __init__
    ===========================================================================
    """

    def test___init___with_worker_init_kwargs(self):
        worker = BaseWorkerHandler(
            worker_class=BaseWorker,
            task_courier_class=RedisClientWorkerTaskCourier,
            worker_init_kwargs={"data": "test", "data2": "test2"},
            test_variable="test_variable_data")
        self.assertEqual(worker.worker_class, BaseWorker)
        self.assertDictEqual(worker.worker_init_kwargs,
                             {"data": "test", "data2": "test2"})
        self.assertEqual(worker.test_variable, "test_variable_data")

    def test___init___without_worker_init_kwargs(self):
        worker = BaseWorkerHandler(
            worker_class=BaseWorker,
            task_courier_class=RedisClientWorkerTaskCourier,
            test_variable="test_variable_data")
        self.assertEqual(worker.worker_class, BaseWorker)
        self.assertIsNone(worker.worker_init_kwargs)
        self.assertEqual(worker.test_variable, "test_variable_data")

    """
    ===========================================================================
    create_worker_instance
    ===========================================================================
    """

    def test_create_worker_instance(self):
        with self.assertRaises(NotImplementedError):
            BaseWorkerHandler().create_worker_instance()

