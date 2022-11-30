import uuid
import pickle
import datetime
import time

from .base import (
    BaseClientTaskHelper,
    BaseWorkerTaskHelper,
    BaseClientWorkerTaskHelper
)


class FullQueueNameMixin:
    """
    Returns full_queue_name (with prefix & sufix, like "pending")
    profides _get_ful_queue_name method.
    """

    prefix_queue = ""

    def _get_ful_queue_name(self, queue_name, sufix=None):
        """Returns full_queue_name (with prefix & sufix, like "pending")"""
        full_queue_name = queue_name
        if self.prefix_queue:
            full_queue_name = f"{self.prefix_queue}:{full_queue_name}"
        if sufix:
            full_queue_name = f"{full_queue_name}:{sufix}"
        return full_queue_name


class RedisClientTaskHelper(FullQueueNameMixin, BaseClientTaskHelper):
    """
    Class for the client side of task helpers using redis.

    The inherited class should provide the ability to:
    - Client side:
        - to add task objects (not only as functions) to the queue;
        - wait for the result;
    """

    refresh_timeout = 0.1

    def __init__(self, redis_connection):
        self.redis_connection = redis_connection

    def get_task_result(
            self, queue_name, task_id, delete_data=True, timeout=None):
        """Waits for the task result to appear, and then returns it.
        Blocking method. Checks every self.refresh_timeout seconds for
        a result availability.
        Client side method.

        * queue_name - queue name, used in the add_task_to_queue method.
        * task_id - id of the task that the add_task_to_queue method returned.
        * delete_data - Whether to remove data from the queue after retrieving.
          default is True.
        * timeout - timeout to wait for the result in seconds or as an
          datetime.timedelta object. Default is None (Waiting forever until it
          appears. If specified - raised TimeoutError if time is up)"""

        utc_start_time = datetime.datetime.utcnow()
        if isinstance(timeout, int) or isinstance(timeout, float):
            timeout = datetime.timedelta(seconds=timeout)
        name = self._get_ful_queue_name(queue_name, "results:") + str(task_id)
        exists = self.redis_connection.exists(name)
        while not exists:
            time.sleep(self.refresh_timeout)
            if timeout:
                if utc_start_time + timeout < datetime.datetime.utcnow():
                    raise TimeoutError
            exists = self.redis_connection.exists(name)

        if delete_data:
            raw_data = self.redis_connection.getdel(name=name)
        else:
            raw_data = self.redis_connection.get(name=name)
        return pickle.loads(raw_data)

    def add_task_to_queue(self, queue_name, task_data):
        """Adds a task to the redis queue for processing. Returns task_id.
        Client side method.

        * queue_name - queue name, used in the add_task_to_queue method.
        * task_data - task objects, what will be added to redis qeueue."""

        task_id = uuid.uuid1()
        task = pickle.dumps((task_id, task_data))
        self.redis_connection.rpush(
            self._get_ful_queue_name(queue_name=queue_name, sufix="pending"),
            task)
        return task_id
