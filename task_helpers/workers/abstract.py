from typing import List, Tuple

from task_helpers.couriers.abstract import AbstractWorkerTaskCourier


class AbstractWorker:
    """
    An abstract class for task processing.
    """

    def __init__(
            self, task_courier: AbstractWorkerTaskCourier, *args, **kwargs):
        """
        Initializations. task_courier (AbstractWorkerTaskCourier instance)
        is required
        """
        self.task_courier = task_courier

    def wait_for_tasks(self) -> List[Tuple]:
        """
        Abstract method. Should return a list of tasks:
        [(task_id, task_data), (task_id, task_data), ...]
        """
        raise NotImplementedError

    def perform_tasks(self, tasks: List[Tuple]) -> List[Tuple]:
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        raise NotImplementedError

    def return_task_results(self, tasks: List[Tuple]) -> None:
        """
        Abstract method for returning task results. Tasks like:
        [(task_id, task_data), (task_id, task_data), ...]
        """
        raise NotImplementedError

    def perform(self, total_iterations: int) -> None:
        """
        Abstract method for starting a worker.
        """
        raise NotImplementedError
