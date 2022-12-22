from typing import List

from task_helpers.tasks import Task


class AbstractWorker:
    """
    An abstract class for task processing.
    """

    def wait_for_tasks(self, *args, **kwargs) -> List(Task):
        """
        Abstract method. Should return a list of tasks as a list.
        """
        raise NotADirectoryError

    def perform_tasks(self, tasks: List(Task), *args, **kwargs) -> List(Task):
        """
        Abstract method for processing tasks.
        """
        raise NotImplementedError

    def return_task_results(self, tasks: List(Task), *args, **kwargs) -> None:
        """
        Abstract method for returning task results.
        """
        raise NotImplementedError

    def perform(self, total_iterations: int, *args, **kwargs) -> None:
        """
        Abstract method for starting a worker.
        """
        raise NotImplementedError
