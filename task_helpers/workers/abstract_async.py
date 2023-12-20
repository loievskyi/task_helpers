from typing import List, Tuple, Awaitable

from task_helpers.couriers.abstract_async import AbstractAsyncWorkerTaskCourier


class AbstractAsyncWorker:
    """
    An abstract class for task processing.
    """

    def __init__(
            self, async_task_courier: AbstractAsyncWorkerTaskCourier,
            *args, **kwargs):
        """
        Initializations. async_task_courier
        (AbstractAsyncWorkerTaskCourier instance) is required
        """
        self.async_task_courier = async_task_courier

    async def wait_for_tasks(self) -> Awaitable[List[Tuple]]:
        """
        Abstract method. Should return a list of tasks:
        [(task_id, task_data), (task_id, task_data), ...]
        """
        raise NotImplementedError

    async def perform_tasks(self, tasks: List[Tuple]) -> Awaitable[List[Tuple]]:
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        raise NotImplementedError

    async def async_init(self):
        """
        Abstract aync init method for initialization async objects
        (aiohttp.ClientSession, for example).
        Calls at the beginning of the "perform" method.
        """
        raise NotImplementedError

    async def async_destroy(self):
        """
        Abstract async destroy method for destroy async objects
        (aiohttp.ClientSession().close, for example).
        Calls at the end of the "perform" method.
        """
        raise NotImplementedError

    async def return_task_results(self, tasks: List[Tuple]) -> Awaitable[None]:
        """
        Abstract method for returning task results. Tasks like:
        [(task_id, task_data), (task_id, task_data), ...]
        """
        raise NotImplementedError

    async def perform(self, total_iterations: int) -> Awaitable[None]:
        """
        Abstract method for starting a worker.
        """
        raise NotImplementedError
