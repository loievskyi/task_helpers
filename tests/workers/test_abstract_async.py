import unittest
import uuid
import asyncio

from task_helpers.couriers.abstract_async import AbstractAsyncWorkerTaskCourier
from task_helpers.workers.abstract_async import AbstractAsyncWorker


class AbstractAsyncWorkerTestCadse(unittest.TestCase):
    """
    Tests to make sure that AbstractAsyncWorker is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.async_task_courier = AbstractAsyncWorkerTaskCourier()
        self.worker = AbstractAsyncWorker(
            async_task_courier=self.async_task_courier)

    def test___init__(self):
        worker = AbstractAsyncWorker(
            async_task_courier=self.async_task_courier)
        self.assertIsInstance(worker, AbstractAsyncWorker)

    def test_wait_for_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.wait_for_tasks()
            )

    def test_perform_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.perform_tasks(tasks=[(uuid.uuid1(), "task_data")])
            )

    def test_return_tasks_results(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.return_tasks_results(
                    tasks=[(uuid.uuid1(), "task_result")])
            )

    def test_async_init(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.async_init()
            )

    def test_async_destroy(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.async_destroy()
            )

    def test_perform(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            asyncio.run(
                self.worker.perform(total_iterations=15)
            )
