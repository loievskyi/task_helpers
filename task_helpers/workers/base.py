import time
import logging

from task_helpers import exceptions


class BaseWorker:
    """
    Base class for workers.
    Initialization requires an instance of task_courier.
    The other kwargs will override the class fields for the current instance
    of the class. They can also be overriden in an inherited class.

    Class fields:
    - task_courier - an instance of the task_courier.
      Specified when the class is initialized.
    - queue_name - The name of the queue from which tasks are read.
    - after_iteration_sleep_time - Downtime in seconds after each task is
      completed (e.g. 0.1). Default is 1 millisecond.
    - return_task_result - True if needs to return the result of the
      task execution, or False otherwise.
    """

    task_courier = None
    queue_name = None
    after_iteration_sleep_time = 0.001
    return_task_result = True

    def __init__(self, task_courier, **kwargs):
        self.task_courier = task_courier
        for key, value in kwargs.items():
            setattr(self, key, value)

    def perform_task(self, task):
        """
        Task processing class. Must be overridden in the inherited class.
        """
        raise NotImplementedError

    def perform(self, total_tasks=1000):
        """
        The main method that starts the task worker.
        Takes a task from the queue, calls the "perform_task method",
        and returns the result if "return_task_result" field is True.

        - total_tasks - how many tasks should the worker perform.
        """
        for num_task in range(total_tasks):
            task = self.task_courier.wait_for_task(queue_name=self.queue_name)
            try:
                task_result = self.perform_task(task)
            except Exception as ex:
                logging.error(f"An error has occured on "
                              f"Worker.perform.perform_task: {ex}")
                if self.return_task_result:
                    self.task_courier.return_task_result(
                        queue_name=self.queue_name,
                        task_id=task[0],
                        task_data=exceptions.PerformTaskError)
            else:
                if self.return_task_result:
                    self.task_courier.return_task_result(
                        queue_name=self.queue_name,
                        task_id=task_result[0],
                        task_data=task_result[1])
            time.sleep(self.after_iteration_sleep_time)
