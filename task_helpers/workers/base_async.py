import logging
import asyncio

from task_helpers.workers.abstract_async import AbstractAsyncWorker
from task_helpers.couriers.abstract_async import AbstractAsyncWorkerTaskCourier
from task_helpers import exceptions


class BaseAsyncWorker(AbstractAsyncWorker):
    """
    Base class for async workers.
    Initialization requires an instance of async_task_courier.
    The other kwargs will override the class fields for the current instance
    of the class. They can also be overriden in an inherited class.

    Class fields:
    - async_task_courier - an instance of the AbstractAsyncWorkerTaskCourier.
      Specified when the class is initialized.
    - queue_name - The name of the queue from which tasks will be performed.
    - after_iteration_sleep_time - Downtime in seconds after each task is
      completed (e.g. 0.1). Default is 1 millisecond.
    - empty_queue_sleep_time - downtime in seconds if the task queue is empty.
      Default is 0.1 seconds.
    - max_tasks_per_iteration - How many tasks can be processed in 1 iteration
      (in the perform_many_tasks method). Influences how many maximum tasks
      will be popped from the queue.
    - needs_result_returning - True if needs to return the result of the
      task performing, or False otherwise.
    """

    async_task_courier: AbstractAsyncWorkerTaskCourier = None
    queue_name = None
    after_iteration_sleep_time = 0.001
    empty_queue_sleep_time = 0.1
    max_tasks_per_iteration = 1
    needs_result_returning = True
    max_simultaneous_tasks = 100
    max_tasks_sleep_time = 0.01

    def __init__(self, async_task_courier: AbstractAsyncWorkerTaskCourier,
                 **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.async_task_courier = async_task_courier
        self.perform_tasks_coros = set()

    async def wait_for_tasks(self):
        """
        Waits for tasks in the queue, pops and returns them. The count of
        tasks depends on the self.max_tasks_per_iteration argument:
        Count of tasks = min(len_queue, self.max_tasks_per_iteration).
        """
        while True:
            tasks = await self.async_task_courier.bulk_get_tasks(
                queue_name=self.queue_name,
                max_count=self.max_tasks_per_iteration)
            if tasks:
                return tasks
            await asyncio.sleep(self.empty_queue_sleep_time)

    async def perform_tasks(self, tasks):
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        output_tasks = []
        for task in tasks:
            task_id, task_data = task
            try:
                output_task = task_id, await self.perform_single_task(task)
                output_tasks.append(output_task)
            except Exception as ex:
                task_result = exceptions.PerformTaskError(
                    task=task, exception=ex)
                output_tasks.append((task_id, task_result))
        return output_tasks

    async def perform_single_task(self, task):
        """
        Abstract method for processing one task.
        Task is tuple: (task_id, task_data). Should return a task resut.
        """
        raise NotImplementedError

    async def return_task_results(self, tasks):
        """
        Method method for sending task results to the clients.
        """
        await self.async_task_courier.bulk_return_task_results(
            queue_name=self.queue_name,
            tasks=tasks,
        )

    async def async_init(self):
        """
        Aync init method for initialization async objects
        (aiohttp.ClientSession, for example).
        Calls at the beginning of the "perform" method.
        """
        pass

    async def async_destroy(self):
        """
        Async destroy method for destroy async objects
        (aiohttp.ClientSession().close, for example).
        Calls at the end of the "perform" method.
        """
        pass

    async def _async_perform_inner(self, input_tasks):
        try:
            output_tasks = await self.perform_tasks(tasks=input_tasks)
        except Exception as ex:
            logging.error(
                f"An error has occured on Worker._async_perform_inner: {ex}")
            output_tasks = list()
            for task in input_tasks:
                task_id = task[0]
                task_result_data = exceptions.PerformTaskError(
                    task=task, exception=ex)
                output_tasks.append((task_id, task_result_data))

        if self.needs_result_returning:
            await self.return_task_results(tasks=output_tasks)

        while True:
            try:
                self.perform_tasks_coros.remove(asyncio.current_task())
            except Exception:
                await asyncio.sleep(self.max_tasks_sleep_time)

    async def perform(self, total_iterations):
        """
        The main method that starts the task worker.
        Takes a task from the queue, calls the "perform_tasks" method,
        and returns the result if "needs_result_returning" field is True.

        - total_iterations - how many iterations should the worker perform.
        """
        await self.async_init()

        for num_task in range(total_iterations):
            while len(self.perform_tasks_coros) >= self.max_simultaneous_tasks:
                await asyncio.sleep(self.max_tasks_sleep_time)
            input_tasks = await self.wait_for_tasks()
            coro = asyncio.create_task(self._async_perform_inner(input_tasks))
            self.perform_tasks_coros.add(coro)
            await asyncio.sleep(self.after_iteration_sleep_time)

        while len(self.perform_tasks_coros) > 0:
            await asyncio.sleep(self.after_iteration_sleep_time)

        await self.async_destroy()
