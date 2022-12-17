import uuid
import unittest

from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.workers.base import BaseWorker
from task_helpers import exceptions
from ..mixins import RedisSetupMixin


class BaseWorkerTestCadse(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that BaseClientTaskCourier is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.task_courier = RedisClientWorkerTaskCourier(self.redis_connection)
        self.base_worker = BaseWorker(task_courier=self.task_courier)

    def test___init__(self):
        worker = BaseWorker(task_courier=self.task_courier, zxc="text",
                            queue_name="new_test_queue_name")
        self.assertEqual(worker.task_courier, self.task_courier)
        self.assertEqual(worker.zxc, "text")
        self.assertEqual(worker.queue_name, "new_test_queue_name")

    def test_perform_task(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.base_worker.perform_task((uuid.uuid1(), "task_data"))

    def test_perform_if_no_exception(self):
        def perform_task(task):
            task_id, task_data = task
            return str(task_data) + "text"

        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.base_worker.perform_task = perform_task
        self.base_worker.queue_name = queue_name

        self.base_worker.perform(total_tasks=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(task_result, str(task_data) + "text")

    class CustomException(Exception):
        def __init__(self, text=None):
            self.text = text

    def test_perform_if_exception(self):

        def perform_task(task):
            raise self.CustomException(text="new custom ex text")

        queue_name = "test_perform_if_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.base_worker.perform_task = perform_task
        self.base_worker.queue_name = queue_name

        self.base_worker.perform(total_tasks=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(type(task_result), exceptions.PerformTaskError)
        self.assertEqual(type(task_result.exception), self.CustomException)
        self.assertEqual(task_result.exception.text, "new custom ex text")

    def test_perform_if_return_task_result_True(self):
        def perform_task(task):
            task_id, task_data = task
            return str(task_data) + "text"

        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.base_worker.perform_task = perform_task
        self.base_worker.queue_name = queue_name
        self.base_worker.return_task_result = True

        self.base_worker.perform(total_tasks=1)
        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)
        task_result = self.task_courier.get_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(exists_task_result, True)
        self.assertEqual(task_result, str(task_data) + "text")

    def test_perform_if_return_task_result_False(self):
        def perform_task(task):
            task_id, task_data = task
            return str(task_data) + "text"

        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.base_worker.perform_task = perform_task
        self.base_worker.queue_name = queue_name
        self.base_worker.return_task_result = False

        self.base_worker.perform(total_tasks=1)
        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)
        with self.assertRaises(exceptions.TaskResultDoesNotExist):
            self.task_courier.get_task_result(
                queue_name=queue_name,
                task_id=task_id)

        self.assertEqual(exists_task_result, False)

    # def test_perform_after_iteration_sleep_time(self):
    #     pass
    #
    # def test_perform_total_tasks(self):
    #     pass

    # GITHUB ISSUE https://github.com/loievskyi/task_helpers/issues/1
    # def test_perform_if_exception(self):
    #     class CustomException(Exception):
    #         def __init__(self, text=None):
    #             self.text = text
    #
    #     def perform_task(task):
    #         raise CustomException(text="new custom ex text")
    #
    #     queue_name = "test_perform_if_exception"
    #     task_data = "test_task_data"
    #     task_id = self.task_courier.add_task_to_queue(
    #         queue_name=queue_name,
    #         task_data=task_data)
    #
    #     # monkey patching
    #     self.base_worker.perform_task = perform_task
    #     self.base_worker.queue_name = queue_name
    #
    #     self.base_worker.perform(total_tasks=1)
    #     task_result = self.task_courier.wait_for_task_result(
    #         queue_name=queue_name,
    #         task_id=task_id)
    #
    #     self.assertEqual(type(task_result), exceptions.PerformTaskError)
    #     self.assertEqual(type(task_result.exception), CustomException)
    #     self.assertEqual(task_result.exception.text, "new custom ex text")
