import uuid
import unittest

from task_helpers.couriers.abstract import (
    AbstractClientTaskCourier,
    AbstractWorkerTaskCourier,
    AbstractClientWorkerTaskCourier,
)


class AbstractClientTaskCourierTestCase(unittest.TestCase):
    """
    Tests to make sure that AbstractClientTaskCourier is working correctly.
    """

    def setUp(self):
        self.task_courier = AbstractClientTaskCourier()

    def test_get_task_result(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.get_task_result(
                queue_name="queue_name",
                task_id=uuid.uuid1())

    def test_wait_for_task_result(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.wait_for_task_result(
                queue_name="queue_name",
                task_id=uuid.uuid1())

    def test_add_task_to_queue(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.add_task_to_queue(
                queue_name="queue_name",
                task_data="task_data")

    def test_bulk_add_tasks_to_queue(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.bulk_add_tasks_to_queue(
                queue_name="queue_name",
                tasks_data=["task_data"])

    def test_check_for_done(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.check_for_done(
                queue_name="queue_name",
                task_id=uuid.uuid1())


class AbstractWorkerTaskCourierTestCase(unittest.TestCase):
    """
    Tests to make sure that AbstractWorkerTaskCourier is working correctly.
    """

    def setUp(self):
        self.task_courier = AbstractWorkerTaskCourier()

    def test_bulk_get_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.bulk_get_tasks(
                queue_name="queue_name",
                max_count=100,
            )

    def test_get_task(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.get_task(queue_name="queue_name")

    def test_wait_for_task(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.wait_for_task(queue_name="queue_name")

    def test_return_task_result(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.task_courier.return_task_result(
                queue_name="queue_name",
                task_id=uuid.uuid1(),
                task_result="task_result")

    def test_bulk_return_task_results(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            task = (uuid.uuid1(), "task_result")
            self.task_courier.bulk_return_task_results(
                queue_name="queue_name",
                tasks=[task]
            )


class AbstractClientWorkerTaskCourierTestCase(
        AbstractClientTaskCourierTestCase,
        AbstractWorkerTaskCourierTestCase,
        unittest.TestCase):
    """
    Tests to make sure that AbstractClientWorkerTaskCourier
    is working correctly.
    """

    def setUp(self):
        self.task_courier = AbstractClientWorkerTaskCourier()
