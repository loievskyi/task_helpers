import uuid
import unittest

from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.workers.classic import ClassicWorker
from ..mixins import RedisSetupMixin


class ClassicWorkerTestCase(RedisSetupMixin, unittest.TestCase):
    """
    Tests to make sure that ClassicWorker is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.queue_name = "test_queue_name"
        self.task_courier = RedisClientWorkerTaskCourier(self.redis_connection)
        self.worker = ClassicWorker(task_courier=self.task_courier)

        # monkey patching
        self.worker.queue_name = self.queue_name
        self.worker.max_tasks_per_iteration = 1

    def generate_input_task(self, task_data=None):
        task_id = uuid.uuid4()
        if task_data is None:
            task_data = {
                "function": self.task_function,
                "args": ("arg_text",),
                "kwargs": {"kwarg1": "kwarg_text"},
            }
        return (task_id, task_data)

    @staticmethod
    def task_function(arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    @staticmethod
    def task_function_without_args_and_kwargs():
        return "example text"

    def task_method(self, arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    """
    ===========================================================================
    perform_tasks
    ===========================================================================
    """

    def test_perform_tasks_if_all_ok(self):
        input_tasks = [self.generate_input_task() for _ in range(5)]
        output_tasks = self.worker.perform_tasks(tasks=input_tasks)

        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    def test_perform_tasks_as_FIFO(self):
        input_tasks = []
        for num in range(5):
            task_data = {
                "function": self.task_function,
                "args": (f"arg_text_{num}",),
                "kwargs": {"kwarg1": f"kwarg_text_{num}"},
            }
            input_tasks.append(self.generate_input_task(task_data=task_data))

        output_tasks = self.worker.perform_tasks(tasks=input_tasks)

        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for num, task in enumerate(output_tasks):
            self.assertEqual(task[1], f"arg_text_{num}kwarg_text_{num}")

    def test_perform_tasks_if_task_data_is_not_dict_instance(self):
        input_tasks = [self.generate_input_task(task_data=123)]
        with self.assertRaises(AssertionError):
            self.worker.perform_tasks(tasks=input_tasks)

    def test_perform_tasks_if_task_data_doesnt_have_the_function_key(self):
        task_data = {
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        with self.assertRaises(AssertionError):
            self.worker.perform_tasks(tasks=input_tasks)

    def test_perform_tasks_if_task_data_without_function_args_and_kwargs(self):
        task_data = {
            "function": self.task_function_without_args_and_kwargs,
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = self.worker.perform_tasks(tasks=input_tasks)

        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "example text")

    def test_perform_tasks_if_task_data_function_is_class_method(self):
        # self are ignored

        task_data = {
            "function": self.task_method,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = self.worker.perform_tasks(tasks=input_tasks)

        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    """
    ===========================================================================
    perform
    ===========================================================================
    """

    def test_perform(self):
        queue_name = "test_perform"
        task_data = {
            "function": self.task_function,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = True

        self.worker.perform(total_iterations=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(task_result, "arg_textkwarg_text")
