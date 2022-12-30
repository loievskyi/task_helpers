import uuid
import pickle
import datetime
import time

from .abstract import (
    AbstractClientTaskCourier,
    AbstractWorkerTaskCourier,
    AbstractClientWorkerTaskCourier
)
from .. import exceptions

__all__ = [
    "FullQueueNameMixin",
    "RedisClientTaskCourier",
    "RedisWorkerTaskCourier",
    "RedisClientWorkerTaskCourier",
]


class FullQueueNameMixin:
    """
    Returns full_queue_name (with prefix & sufix, like "pending")
    profides _get_full_queue_name method.
    """

    prefix_queue = ""

    def _get_full_queue_name(self, queue_name, sufix=None):
        """Returns full_queue_name (with prefix & sufix, like "pending")"""
        full_queue_name = queue_name
        if self.prefix_queue:
            full_queue_name = f"{self.prefix_queue}:{full_queue_name}"
        if sufix:
            full_queue_name = f"{full_queue_name}:{sufix}"
        return full_queue_name


class RedisClientTaskCourier(FullQueueNameMixin, AbstractClientTaskCourier):
    """
    Class for the client side of task helpers using redis.

    Client side methods:
        - get_task_result - returns task retuls, if it exists.
        - wait_for_task_result - Waits for the task result to appear.
        - add_task_to_queue - adds a task to the redis queue for processing.
        - check_for_done - Checks if the task has completed.
    """

    refresh_timeout = 0.1

    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def _generate_task_id(self):
        return uuid.uuid1()

    def get_task_result(self, queue_name, task_id, delete_data=True):
        """Returns task retult, if it exists.
        Otherwise, raises exceptions.TaskResultDoesNotExist. If an error occurs
        during the execution of the task returns exceptions.PerformTaskError.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        - delete_data - Whether to remove data from the queue after retrieving.
          default is True."""

        name = self._get_full_queue_name(queue_name, "results:") + str(task_id)
        if delete_data:
            raw_data = self.redis_connection.getdel(name=name)
        else:
            raw_data = self.redis_connection.get(name=name)
        if raw_data is None:
            raise exceptions.TaskResultDoesNotExist
        return pickle.loads(raw_data)

    def wait_for_task_result(
            self, queue_name, task_id, delete_data=True, timeout=None):
        """Waits for the task result to appear, and then returns it. Blocking
        method. Checks every self.refresh_timeout seconds for a result.
        Raises TimeoutError in case of timeout. If an error occurs during the
        execution of the task raises exceptions.PerformTaskError.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        - delete_data - Whether to remove data from the queue after retrieving.
          default is True.
        - timeout - timeout to wait for the result in seconds or as an
          datetime.timedelta object. Default is None (wait indefinitely until
          it appears). If specified - raises TimeoutError if time is up"""

        utc_start_time = datetime.datetime.utcnow()
        if isinstance(timeout, int) or isinstance(timeout, float):
            timeout = datetime.timedelta(seconds=timeout)
        first_iteration = True
        while first_iteration or not timeout or \
                utc_start_time + timeout > datetime.datetime.utcnow():
            try:
                first_iteration = False
                return self.get_task_result(
                    queue_name=queue_name,
                    task_id=task_id,
                    delete_data=delete_data)
            except exceptions.TaskResultDoesNotExist:
                time.sleep(self.refresh_timeout)
        raise TimeoutError

    def add_task_to_queue(self, queue_name, task_data):
        """Adds a task to the redis queue for processing. Returns task_id.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_data - task objects, what will be added to redis qeueue."""

        task_id = self._generate_task_id()
        task = pickle.dumps((task_id, task_data))
        self.redis_connection.rpush(
            self._get_full_queue_name(queue_name=queue_name, sufix="pending"),
            task)
        return task_id

    def check_for_done(self, queue_name, task_id):
        """Checks if the task has completed.
        Returns True - if task is done (successful or unsuccessful),
        or False if there is no task result yet."""

        name = self._get_full_queue_name(queue_name, "results:") + str(task_id)
        return bool(self.redis_connection.exists(name))


class RedisWorkerTaskCourier(FullQueueNameMixin, AbstractWorkerTaskCourier):
    """
    Class for the worker side of task helpers using redis.

    Worker side methods:
        - get_tasks - pops tasks from queue and returns it.
        - get_task - returns one task from redis queue.
        - wait_for_task - waits for task and returns it.
        - return_task_result - returns result to the client side via redis.
    """

    result_timeout = 600  # Set None to keep task_result permanently.

    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def get_tasks(self, queue_name, max_count):
        """Pops tasks from queue and returns it. The number of task which
        depends on max_count and the number of elements in the queue.
        Worker side method.

        Task is tuple of (task_id, task_data). The result like
        [(task_id, task_data), (task_id, task_data), ...].

        - queue_name - queue name, used in the add_task_to_queue method.
        - max_count - the maximum number of tasks that can be extracted from
          the queue"""

        tasks = self.redis_connection.lpop(
            self._get_full_queue_name(queue_name=queue_name, sufix="pending"),
            count=max_count)
        if tasks:
            return [pickle.loads(task) for task in tasks]
        return []

    def get_task(self, queue_name):
        """Returns one task from redis queue as tuple (task_id, task_data).
        If task doesn't exists, raises exceptions.TaskDoesNotExist.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method."""

        task = self.redis_connection.lpop(
            self._get_full_queue_name(queue_name, "pending")
        )
        if task is None:
            raise exceptions.TaskDoesNotExist
        task_id, task_data = pickle.loads(task)
        return task_id, task_data

    def wait_for_task(self, queue_name, timeout=None):
        """Returns one task from redis queue as tuple (task_id, task_data).
        If timeout is None (default), then waits task indefinitely.
        Raises TimeoutError in case of timeout.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - timeout - timeout to wait for the task in seconds. Default is None
          (Waiting forever until it appears). If specified - raised
          TimeoutError if time is up"""

        task = self.redis_connection.blpop(
            self._get_full_queue_name(queue_name, "pending"),
            timeout=timeout)
        if task is None:
            raise TimeoutError
        task_id, task_data = pickle.loads(task[-1])
        return task_id, task_data

    def return_task_result(self, queue_name, task_id, task_result):
        """Return the result of processing the task to the client via redis.
        Worker side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task.
        - task_data - task objects, what will be returned to the client."""

        name = self._get_full_queue_name(
            queue_name=queue_name, sufix="results:") + str(task_id)
        value = pickle.dumps(task_result)
        self.redis_connection.set(name=name, value=value,
                                  ex=self.result_timeout)


class RedisClientWorkerTaskCourier(
        RedisClientTaskCourier,
        RedisWorkerTaskCourier,
        AbstractClientWorkerTaskCourier):
    """
    Class for the client and worker sides of task helpers, works via redis.

    Client side methods:
        - get_task_result - returns task retuls, if it exists.
        - wait_for_task_result - Waits for the task result to appear.
        - add_task_to_queue - adds a task to the redis queue for processing.
        - check_for_done - Checks if the task has completed.

    Worker side methods:
        - get_tasks - pops tasks from queue and returns it.
        - get_task - returns one task from redis queue.
        - wait_for_task - waits for task and returns it.
        - return_task_result - returns result to the client side via redis.
    """
    pass
