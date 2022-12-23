class AbstractWorker:
    """
    An abstract class for task processing.
    """

    def wait_for_tasks(self) -> list(tuple):
        """
        Abstract method. Should return a list of tasks:
        [(task_id, task_data), (task_id, task_data), ...]
        """
        raise NotADirectoryError

    def perform_tasks(self, tasks: list(tuple)) -> list(tuple):
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        raise NotImplementedError

    def return_task_results(self, tasks: list(tuple)) -> None:
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
