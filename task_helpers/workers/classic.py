from .base import BaseWorker


class ClassicWorker(BaseWorker):
    """
    Сlassic worker, where the task is a tuple: (task_id, task_data).
    task_data is a dictionary with keys "function", "args" and "kwargs".
    Arguments "args" and "kwargs" are optional.

    Class fields:
    - task_courier - an instance of the task_courier.
      Specified when the class is initialized.
    - queue_name - The name of the queue from which tasks are read.
    - after_iteration_sleep_time - Downtime in seconds after each task is
      completed (e.g. 0.1). Default is 1 millisecond.
    - return_task_result - True if needs to return the result of the
      task execution, or False otherwise.
    """

    def perform_task(self, task):
        """
        task is a tuple: (task_id, task_data).
        task_data is a dictionary with keys "function", "args" and "kwargs".
        Calls a function with args "args" and kwargs "kwargs", unpacking them,
        and returns the execution result. Arguments "args" and "kwargs" are
        optional.
        """
        task_id, task_data = task
        function = task_data["function"]
        function_args = task_data.get("args", tuple())
        function_kwargs = task_data.get("kwargs", dict())
        return function(*function_args, **function_kwargs)
