import unittest
import uuid

from task_helpers.couriers.abstract import AbstractWorkerTaskCourier
from task_helpers.workers.abstract import AbstractWorker


class AbstractWorkerTestCadse(unittest.TestCase):
    """
    Tests to make sure that AbstractWorker is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.task_courier = AbstractWorkerTaskCourier()
        self.worker = AbstractWorker(task_courier=self.task_courier)

    def test___init__(self):
        worker = AbstractWorker(task_courier=self.task_courier)
        self.assertIsInstance(worker, AbstractWorker)

    def test_wait_for_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.wait_for_tasks()

    def test_perform_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.perform_tasks(tasks=[(uuid.uuid1(), "task_data")])

    def test_return_task_results(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.return_task_results(
                tasks=[(uuid.uuid1(), "task_result")])

    def test_perform(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.perform(total_iterations=15)
