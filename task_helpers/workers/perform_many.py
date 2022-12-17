import time
import logging

from task_helpers.workers.base import BaseWorker
from task_helper import exceptions


class PerformManyWorker(BaseWorker):
    """
    A worker that can process many tasks at once.

    Class fields:
    - task_courier - an instance of the task_courier.
      Specified when the class is initialized.
    - queue_name - The name of the queue from which tasks are read.
    - after_iteration_sleep_time - downtime in seconds after each task is
      completed (e.g. 0.1). Default is 1 millisecond.
    - return_task_result - True if needs to return the result of the
      task execution, or False otherwise.
    - empty_queue_sleep_time - downtime in seconds if the task queue is empty.
      Default is 0.1 seconds.
    - max_tasks_per_iteration - How many tasks can be processed in 1 iteration
      (in the perform_many_tasks method). Influences how many maximum tasks
      will be popped from the queue.
    """

    empty_queue_sleep_time = 0.1
    max_tasks_per_iteration = 100

    def perform_many_tasks(self, tasks):
        """
        Tasks processing class.

        tasks are list of tuples:
        [(task_id, task_data), (task_id, task_data), ... ]

        Returns task retuls as list of tuples:
        [(task_id, task_result), (task_id, task_result), ... ]

        Must be overridden in the inherited class.
        """
        raise NotImplementedError

    def wait_for_tasks(self):
        """
        Waits for tasks in the queue, pops and returns them. The count of
        tasks depends on the self.max_tasks_per_iteration argument.
        """
        while True:
            tasks = self.task_courier.get_tasks(
                queue_name=self.queue_name,
                max_count=self.max_tasks_per_iteration)
            if tasks:
                break
            time.sleep(self.empty_queue_sleep_time)

    def perform(self, total_iterations):
        """
        The main method that starts the task worker.
        Takes a task from the queue, calls the "perform_many_task method",
        and returns the result if "return_task_result" field is True.

        - total_iterations - how many iterations should the worker perform.
        """
        for num_task in range(total_iterations):
            tasks = self.wait_for_tasks()
            try:
                task_id_result_tuples = self.perform_many_tasks(tasks)
            except Exception as ex:
                logging.error(f"An error has occured on "
                              f"Worker.perform.perform_many_tasks: {ex}")
                task_id_result_tuples = [(task_id, exceptions.PerformTaskError)
                                         for task_id, task_data in tasks]

            if self.return_task_result:
                for task_id, task_result in task_id_result_tuples:
                    self.task_courier.return_task_result(
                        queue_name=self.queue_name,
                        task_id=task_id,
                        task_result=task_result)

            time.sleep(self.after_iteration_sleep_time)
