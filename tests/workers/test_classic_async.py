import uuid
import unittest

from task_helpers.couriers.redis_async import RedisAsyncClientWorkerTaskCourier
from task_helpers.couriers.redis import RedisClientWorkerTaskCourier
from task_helpers.workers.classic_async import ClassicAsyncWorker
from ..mixins import RedisSetupMixin


class ClassicWorkerTestCase(RedisSetupMixin, unittest.IsolatedAsyncioTestCase):
    """
    Tests to make sure that ClassicAsyncWorker is working correctly.
    """

    def setUp(self):
        super().setUp()
        self.queue_name = "test_queue_name"
        self.task_courier = RedisClientWorkerTaskCourier(self.redis_connection)

    async def asyncSetUp(self):
        await super().asyncSetUp()
        self.async_task_courier = RedisAsyncClientWorkerTaskCourier(
            self.aioredis_connection)
        self.worker = ClassicAsyncWorker(
            async_task_courier=self.async_task_courier)

        # monkey patching
        self.worker.queue_name = self.queue_name
        self.worker.max_tasks_per_iteration = 100

    @staticmethod
    def task_function(arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    @staticmethod
    async def async_task_function(arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    def generate_input_task(self, task_data=None, task_function=task_function):
        task_id = uuid.uuid4()
        if task_data is None:
            task_data = {
                "function": self.task_function,
                "args": ("arg_text",),
                "kwargs": {"kwarg1": "kwarg_text"},
            }
        return (task_id, task_data)

    @staticmethod
    def task_function_without_args_and_kwargs():
        return "example text"

    @staticmethod
    async def async_task_function_without_args_and_kwargs():
        return "example text"

    def task_method(self, arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    async def async_task_method(self, arg1, *, kwarg1):
        return str(arg1) + str(kwarg1)

    """
    ===========================================================================
    perform_tasks
    ===========================================================================
    """

    # tested single method
    async def test_perform_tasks_if_all_ok_with_sync_function(self):
        input_tasks = [
            self.generate_input_task(task_function=self.task_function)
            for _ in range(5)
        ]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    async def test_perform_tasks_if_all_ok_with_async_function(self):
        input_tasks = [
            self.generate_input_task(task_function=self.async_task_function)
            for _ in range(5)
        ]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    async def test_perform_tasks_as_FIFO_with_sync_function(self):
        input_tasks = []
        for num in range(5):
            task_data = {
                "function": self.task_function,
                "args": (f"arg_text_{num}",),
                "kwargs": {"kwarg1": f"kwarg_text_{num}"},
            }
            input_tasks.append(self.generate_input_task(task_data=task_data))

        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)

        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for num, task in enumerate(output_tasks):
            self.assertEqual(task[1], f"arg_text_{num}kwarg_text_{num}")

    async def test_perform_tasks_as_FIFO_with_async_function(self):
        input_tasks = []
        for num in range(5):
            task_data = {
                "function": self.async_task_function,
                "args": (f"arg_text_{num}",),
                "kwargs": {"kwarg1": f"kwarg_text_{num}"},
            }
            input_tasks.append(self.generate_input_task(task_data=task_data))

        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 5)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for num, task in enumerate(output_tasks):
            self.assertEqual(task[1], f"arg_text_{num}kwarg_text_{num}")

    # tested single method
    async def test_perform_tasks_if_task_data_without_sync_function_args_and_kwargs(self):
        task_data = {
            "function": self.task_function_without_args_and_kwargs,
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "example text")

    # tested single method
    async def test_perform_tasks_if_task_data_without_async_function_args_and_kwargs(self):
        task_data = {
            "function": self.async_task_function_without_args_and_kwargs,
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "example text")

    # tested single method
    async def test_perform_tasks_if_task_data_function_is_sync_class_method(self):
        # self are ignored

        task_data = {
            "function": self.task_method,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    # tested single method
    async def test_perform_tasks_if_task_data_function_is_async_class_method(self):
        # self are ignored

        task_data = {
            "function": self.async_task_method,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_tasks = [self.generate_input_task(task_data=task_data)]
        output_tasks = await self.worker.perform_tasks(tasks=input_tasks)
        self.assertEqual(len(input_tasks), 1)
        self.assertEqual(len(input_tasks), len(output_tasks))
        for task in output_tasks:
            self.assertEqual(task[1], "arg_textkwarg_text")

    """
    ===========================================================================
    perform_single_task
    ===========================================================================
    """

    async def test_perform_single_task_if_all_ok_with_sync_function(self):
        input_task = self.generate_input_task(task_function=self.task_function)
        output_task_data = await self.worker.perform_single_task(task=input_task)
        self.assertEqual(output_task_data, "arg_textkwarg_text")

    async def test_perform_single_task_if_all_ok_with_async_function(self):
        input_task = self.generate_input_task(
            task_function=self.async_task_function)
        output_task_data = await self.worker.perform_single_task(task=input_task)
        self.assertEqual(output_task_data, "arg_textkwarg_text")

    async def test_perform_single_task_if_task_data_without_sync_function_args_and_kwargs(self):
        task_data = {
            "function": self.task_function_without_args_and_kwargs,
        }
        input_task = self.generate_input_task(task_data=task_data)
        output_task_data = await self.worker.perform_single_task(task=input_task)
        self.assertEqual(output_task_data, "example text")

    async def test_perform_single_task_if_task_data_without_async_function_args_and_kwargs(self):
        task_data = {
            "function": self.async_task_function_without_args_and_kwargs,
        }
        input_task = self.generate_input_task(task_data=task_data)
        output_task_data = await self.worker.perform_single_task(task=input_task)

        self.assertEqual(output_task_data, "example text")

    async def test_perform_single_task_if_task_data_function_is_sync_class_method(self):
        # self are ignored

        task_data = {
            "function": self.task_method,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_task = self.generate_input_task(task_data=task_data)
        output_task_data = await self.worker.perform_single_task(task=input_task)
        self.assertEqual(output_task_data, "arg_textkwarg_text")

    async def test_perform_single_task_if_task_data_function_is_async_class_method(self):
        # self are ignored

        task_data = {
            "function": self.async_task_method,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_task = self.generate_input_task(task_data=task_data)
        output_task_data = await self.worker.perform_single_task(task=input_task)
        self.assertEqual(output_task_data, "arg_textkwarg_text")

    async def test_perform_single_task_if_task_data_doesnt_have_the_function_key(self):
        task_data = {
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        input_task = self.generate_input_task(task_data=task_data)
        with self.assertRaises(AssertionError):
            await self.worker.perform_single_task(task=input_task)

    async def test_perform_single_task_if_task_data_is_not_dict_instance(self):
        input_task = self.generate_input_task(task_data=123)
        with self.assertRaises(AssertionError):
            await self.worker.perform_single_task(task=input_task)

    """
    ===========================================================================
    perform
    ===========================================================================
    """

    async def test_perform_with_sync_function(self):
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

        await self.worker.perform(total_iterations=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(task_result, "arg_textkwarg_text")

    async def test_perform_with_async_function(self):
        queue_name = "test_perform"
        task_data = {
            "function": self.async_task_function,
            "args": ("arg_text",),
            "kwargs": {"kwarg1": "kwarg_text"},
        }
        task_id = self.task_courier.add_task_to_queue(
            queue_name=queue_name,
            task_data=task_data)

        # monkey patching
        self.worker.queue_name = queue_name
        self.worker.needs_result_returning = True

        await self.worker.perform(total_iterations=1)
        task_result = self.task_courier.wait_for_task_result(
            queue_name=queue_name,
            task_id=task_id)

        self.assertEqual(task_result, "arg_textkwarg_text")
