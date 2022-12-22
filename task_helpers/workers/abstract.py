class AbstractWorker:
    """
    An abstract class for task processing.
    """

    def wait_for_tasks(self, *args, **kwargs):
        """
        Abstract method. Should return a list of tasks as a list.
        """
        raise NotADirectoryError

    def perform_tasks(self, tasks, *args, **kwargs):
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        raise NotImplementedError

    def return_task_results(self, tasks, *args, **kwargs):
        """
        Abstract method for returning task results.
        """
        raise NotImplementedError

    def perform(self, total_iterations: int, *args, **kwargs):
        """
        Abstract method for starting a worker.
        """
        raise NotImplementedError
