import time
import logging
from typing import List, Union, Tuple

from task_helpers.couriers.abstract import AbstractWorkerTaskCourier
from task_helpers.workers.abstract import AbstractWorker


class BaseWorker(AbstractWorker):
    """
    Base class for workers.
    Initialization requires an instance of task_courier.
    The other kwargs will override the class fields for the current instance
    of the class. They can also be overriden in an inherited class.

    Class fields:
    - task_courier - an instance of the task_courier.
      Specified when the class is initialized.
    - queue_name - The name of the queue from which tasks will be performed.
    - after_iteration_sleep_time - Downtime in seconds after each task is
      completed (e.g. 0.1). Default is 1 millisecond.
    - empty_queue_sleep_time - downtime in seconds if the task queue is empty.
      Default is 0.1 seconds.
    - max_tasks_per_iteration - How many tasks can be processed in 1 iteration
      (in the perform_many_tasks method). Influences how many maximum tasks
      will be popped from the queue.
    """

    task_courier: AbstractWorkerTaskCourier = None
    queue_name: str = None
    after_iteration_sleep_time: Union(int, float) = 0.001
    empty_queue_sleep_time: Union(int, float) = 0.1
    max_tasks_per_iteration: int = 100

    def __init__(self, task_courier: AbstractWorkerTaskCourier, **kwargs):
        self.task_courier = task_courier
        for key, value in kwargs.items():
            setattr(self, key, value)

    def wait_for_tasks(self) -> List(Tuple):
        """
        Waits for tasks in the queue, pops and returns them. The count of
        tasks depends on the self.max_tasks_per_iteration argument:
        Count of tasks = min(len_queue, self.max_tasks_per_iteration).
        """
        while True:
            tasks = self.task_courier.get_tasks(
                queue_name=self.queue_name,
                max_count=self.max_tasks_per_iteration)
            if tasks:
                return tasks
            time.sleep(self.empty_queue_sleep_time)

    def perform_tasks(self, tasks: List(Tuple)) -> List(Tuple):
        """
        Abstract method for processing tasks. Should return a list of tasks:
        [(task_id, task_result), (task_id, task_result), ...]
        """
        raise NotImplementedError

    def return_task_results(self, tasks: List(Tuple)) -> None:
        """
        Method method for returning task results to the clients.
        """
        if self.needs_result_returning:
            for task_id, task_result in tasks:
                self.task_courier.return_task_result(
                    queue_name=self.queue_name,
                    task_id=task_id,
                    task_result=task_result)

    def perform(self, total_iterations: int) -> None:
        """
        The main method that starts the task worker.
        Takes a task from the queue, calls the "perform_task method",
        and returns the result if "return_task_result" field is True.

        - total_iterations - how many iterations should the worker perform.
        """
        for num_task in range(total_iterations):
            tasks = self.wait_for_tasks()
            try:
                tasks = self.perform_tasks(tasks=tasks)
            except Exception as ex:
                logging.error(f"An error has occured on Worker.perform: {ex}")
            self.return_task_result(tasks=tasks)

            time.sleep(self.after_iteration_sleep_time)
