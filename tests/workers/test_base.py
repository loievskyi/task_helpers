import uuid
import unittest

import timeout_decorator

from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.workers.base import BaseWorker
from task_helpers import exceptions
from ..mixins import RedisSetupMixin


class BaseWorkerTestCase(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that BaseWorker is working correctly.
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

    class CustomException(Exception):
        def __init__(self, text=None):
            self.text = text

    def perform_tasks_monkeypatching_exception(self, tasks):
        raise self.CustomException(text="new custom ex text")

    def perform_tasks_monkeypatching(self, tasks):
        task_results = [(task_id, str(task_data) + "text")
                        for task_id, task_data in tasks]
        return task_results

    """
    ===========================================================================
    __init__
    ===========================================================================
    """

    def test___init__(self):
        worker = BaseWorker(task_courier=self.task_courier,
                            max_tasks_per_iteration=5,
                            test_variable="test_variable_data")
        self.assertEqual(worker.task_courier, self.task_courier)
        self.assertEqual(worker.max_tasks_per_iteration, 5)
        self.assertEqual(worker.test_variable, "test_variable_data")

    """
    ===========================================================================
    wait_for_tasks
    ===========================================================================
    """

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

    """
    ===========================================================================
    perform_tasks
    ===========================================================================
    """

    def test_perform_tasks(self):
        with self.assertRaises(expected_exception=NotImplementedError):
            self.worker.perform_tasks(tasks=[(uuid.uuid1(), "task_data")])

    """
    ===========================================================================
    return_task_results
    ===========================================================================
    """

    def test_return_task_results_if_needs_result_returning_True(self):
        queue_name = "test_return_task_results"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        output_tasks = [(task_id, task_data)]

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = True

        self.worker.return_task_results(tasks=output_tasks)

        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)
        task_result = self.task_courier.get_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertTrue(exists_task_result)
        self.assertEqual(task_result, str(task_data))

    def test_return_task_results_if_needs_result_returning_False(self):
        queue_name = "test_return_task_results"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        output_tasks = [(task_id, task_data)]

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = False

        self.worker.return_task_results(tasks=output_tasks)

        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)

        self.assertFalse(exists_task_result)

    """
    ===========================================================================
    perform
    ===========================================================================
    """

    def test_perform_if_no_exception(self):
        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name

        self.worker.perform(total_iterations=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(task_result, str(task_data) + "text")

    def test_perform_if_exception(self):
        queue_name = "test_perform_if_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching_exception
        self.worker.queue_name = queue_name

        self.worker.perform(total_iterations=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(type(task_result), exceptions.PerformTaskError)
        self.assertEqual(type(task_result.exception), self.CustomException)
        self.assertEqual(task_result.exception.text, "new custom ex text")

    """
    ===========================================================================
    needs_result_returning
    ===========================================================================
    """

    def test_perform_if_needs_result_returning_True(self):
        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = True

        self.worker.perform(total_iterations=1)
        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)
        task_result = self.task_courier.get_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertTrue(exists_task_result)
        self.assertEqual(task_result, str(task_data) + "text")

    def test_perform_if_needs_result_returning_False(self):
        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = False

        self.worker.perform(total_iterations=1)
        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)

        self.assertFalse(exists_task_result)

    """
    ===========================================================================
    after_iteration_sleep_time
    ===========================================================================
    """

    def test_after_iteration_sleep_time(self):
        pass

    """
    ===========================================================================
    empty_queue_sleep_time
    ===========================================================================
    """

    def test_empty_queue_sleep_time(self):
        pass

    """
    ===========================================================================
    max_tasks_per_iteration
    ===========================================================================
    """

    def test_max_tasks_per_iteration_less_then_tasks_in_queue(self):
        before_tasks = []
        for num in range(50):
            task_data = f"task_data_{num}"
            task_id = self.task_courier.add_task_to_queue(
                queue_name=self.queue_name,
                task_data=task_data)
            before_tasks.append((task_id, task_data))

        # monkey patching
        self.worker.max_tasks_per_iteration = 100

        after_tasks = self.worker.wait_for_tasks()
        self.assertEqual(len(after_tasks), 50)
        self.assertListEqual(before_tasks, after_tasks)

    def test_max_tasks_per_iteration_more_then_tasks_in_queue(self):
        before_tasks = []
        for num in range(150):
            task_data = f"task_data_{num}"
            task_id = self.task_courier.add_task_to_queue(
                queue_name=self.queue_name,
                task_data=task_data)
            before_tasks.append((task_id, task_data))

        # monkey patching
        self.worker.max_tasks_per_iteration = 100

        after_tasks = self.worker.wait_for_tasks()
        self.assertEqual(len(after_tasks), 100)
        self.assertListEqual(before_tasks[:100], after_tasks)

    """
    ===========================================================================
    total_iterations
    ===========================================================================
    """

    def test_total_iterations(self):

        queue_name = "test_perform_if_no_exception"
        task_data = "test_task_data"
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.perform_tasks = self.perform_tasks_monkeypatching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = True

        self.worker.perform(total_iterations=1)
        exists_task_result = self.task_courier.check_for_done(
            queue_name=queue_name,
            task_id=task_id)
        task_result = self.task_courier.get_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertTrue(exists_task_result)
        self.assertEqual(task_result, str(task_data) + "text")

    # # GITHUB ISSUE https://github.com/loievskyi/task_helpers/issues/1
    # # def test_perform_if_exception(self):
    # #     class CustomException(Exception):
    # #         def __init__(self, text=None):
    # #             self.text = text
    # #
    # #     def perform_tasks(task):
    # #         raise CustomException(text="new custom ex text")
    # #
    # #     queue_name = "test_perform_if_exception"
    # #     task_data = "test_task_data"
    # #     task_id = self.task_courier.add_task_to_queue(
    # #         queue_name=queue_name,
    # #         task_data=task_data)
    # #
    # #     # monkey patching
    # #     self.worker.perform_tasks = self.perform_tasks
    # #     self.worker.queue_name = queue_name
    # #
    # #     self.worker.perform(total_iterations=1)
    # #     task_result = self.task_courier.wait_for_task_result(
    # #         queue_name=queue_name,
    # #         task_id=task_id)
    # #
    # #     self.assertEqual(type(task_result), exceptions.PerformTaskError)
    # #     self.assertEqual(type(task_result.exception), CustomException)
    # #     self.assertEqual(task_result.exception.text, "new custom ex text")
