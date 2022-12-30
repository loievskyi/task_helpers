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

    max_tasks_per_iteration = 1

    def perform_tasks(self, tasks):
        """
        Method for processing tasks. Returns a list of tasks.
        task is a tuple: (task_id, task_data).
        task_data is a dictionary with keys "function", "args" and "kwargs".
        Calls a function with args "args" and kwargs "kwargs", unpacking them,
        and returns the execution result. Arguments "args" and "kwargs" are
        optional.
        """
        results = []
        for task in tasks:
            task_id, task_data = task
            assert isinstance(task_data, dict), \
                "task_data must be a dict instance."
            assert "function" in task_data.keys(), \
                "task_data must have a \"function\" key."
            function = task_data["function"]
            function_args = task_data.get("args", tuple())
            function_kwargs = task_data.get("kwargs", dict())
            task_result = function(*function_args, **function_kwargs)
            results.append((task_id, task_result))

        return results
