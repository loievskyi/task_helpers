from typing import List, Tuple


class AbstractClientTaskCourier(object):
    """
    Abstract class for the client side of task helpers.

    The inherited class should provide the ability to:
    Client side methods:
        - get_task_result - returns the result of the task, if it exists.
        - wait_for_task_result - waits for the result of the task to appear,
          and then returns it.
        - add_task_to_queue - adds one task to the queue for processing.
        - bulk_add_tasks_to_queue - adds many tasks to the queue for
          processing.
        - check_for_done - сhecks if the task has completed.
    """

    def get_task_result(self, queue_name, task_id, delete_data=True) -> object:
        """Returns the result of the task, if it exists.
        Otherwise, raises exceptions.TaskResultDoesNotExist. If an error occurs
        during the execution of the task, returns exceptions.PerformTaskError.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        - delete_data - Whether to remove data from the queue after retrieving.
          default is True."""
        raise NotImplementedError

    def wait_for_task_result(self, queue_name, task_id, delete_data=True,
                             timeout=None) -> object:
        """Waits for the result of the task to appear, and then returns it.
        Raises TimeoutError in case of timeout. If an error occurs
        during the execution of the task, returns exceptions.PerformTaskError.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        - delete_data - Whether to remove data from the queue after retrieving.
          default is True.
        - timeout - timeout to wait for the result in seconds or as an
          datetime.timedelta object. Default is None (wait indefinitely until
          it appears). If specified - raises TimeoutError if time is up"""
        raise NotImplementedError

    def add_task_to_queue(self, queue_name, task_data) -> object:
        """Adds one task to the queue for processing. Returns task_id.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_data - task objects, what will be added to redis qeueue."""
        raise NotImplementedError

    def bulk_add_tasks_to_queue(self, queue_name, tasks_data) -> List:
        """Adds many tasks to the queue for processing.
        Returns a list of task_ids.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - tasks_data - task objects, what will be added to redis qeueue."""
        raise NotImplementedError

    def check_for_done(self, queue_name, task_id) -> bool:
        """Сhecks if the task has completed.
        Returns True - if task is done (successful or unsuccessful),
        or False if there is no task result yet.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        """
        raise NotImplementedError


class AbstractWorkerTaskCourier(object):
    """
    Abstract class for the worker side of task helpers.

    The inherited class should provide the ability to:
    Worker side methods:
        - get_task - pops one task from the queue and returns it.
        - bulk_get_tasks - pops many tasks from the queue and returns them.
        - wait_for_task - Waits for a task to appear, pops it from the queue,
          and returns it.
        - return_task_result - returns the result of the processing of the task
          to the client side.
        - bulk_return_task_results - returns the results of processing
          multiple tasks to the client side.
    """

    def get_task(self, queue_name) -> Tuple:
        """Pops one task from the queue and returns it.
        Task is a tuple (task_id, task_data)
        If task doesn't exists, raises exceptions.TaskDoesNotExist.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method."""
        raise NotImplementedError

    def bulk_get_tasks(self, queue_name, max_count) -> List[Tuple]:
        """Pops many tasks from the queue and returns them. The number of task
        which depends on max_count and the number of elements in the queue.
        Tasks are [(task_id, task_data), (task_id, task_data), ...].
        If there are no tasks in the queue, it will return an empty list.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - max_count - the maximum number of tasks that can be extracted from
          the queue"""
        raise NotImplementedError

    def wait_for_task(self, queue_name, timeout=None) -> Tuple:
        """Waits for a task to appear, pops it from the queue, and returns it.
        Task is a tuple (task_id, task_data).
        If timeout is None (default), then waits for a task indefinitely.
        Raises TimeoutError in case of timeout.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - timeout - timeout to wait for the task in seconds. Default is None
          (Waiting forever until it appears). If specified - raised
          TimeoutError if time is up"""
        raise NotImplementedError

    def return_task_result(self, queue_name, task_id, task_result) -> None:
        """Returns the result of the processing of the task to the client side.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task.
        - task_result - the result of the processing of the task, what will be
          returned to the client."""
        raise NotImplementedError

    def bulk_return_task_results(self, queue_name, tasks) -> None:
        """Returns the results of processing multiple tasks to the client side.
        Tasks is list of tuples: [(task_id, task_result), ...]
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - tasks - a list of tuples, like [(task_id, task_result), ...]"""
        raise NotImplementedError


class AbstractClientWorkerTaskCourier(
        AbstractWorkerTaskCourier, AbstractClientTaskCourier):
    """
    Abstract class for the client and worker sides of task helpers.
    The inherited class should provide the ability to:

    Client side methods:
        - get_task_result - returns the result of the task, if it exists.
        - wait_for_task_result - waits for the result of the task to appear,
          and then returns it.
        - add_task_to_queue - adds one task to the queue for processing.
        - bulk_add_tasks_to_queue - adds many tasks to the queue for
          processing.
        - check_for_done - сhecks if the task has completed.

    Worker side methods:
        - get_task - pops one task from the queue and returns it.
        - bulk_get_tasks - pops many tasks from the queue and returns them.
        - wait_for_task - Waits for a task to appear, pops it from the queue,
          and returns it.
        - return_task_result - returns the result of the processing of the task
          to the client side.
        - bulk_return_task_results - returns the results of processing
          multiple tasks to the client side.
    """
    pass
