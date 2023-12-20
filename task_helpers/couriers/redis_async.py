import uuid
import pickle
import datetime
# import time
import asyncio

from .abstract_async import (
    AbstractAsyncClientTaskCourier,
    AbstractAsyncWorkerTaskCourier,
    AbstractAsyncClientWorkerTaskCourier
)
from .. import exceptions

__all__ = [
    "FullQueueNameMixin",
    "RedisAsyncClientTaskCourier",
    "RedisAsyncWorkerTaskCourier",
    "RedisAsyncClientWorkerTaskCourier",
]


class FullQueueNameMixin:
    """
    Returns full_queue_name (with prefix & sufix, like "pending")
    profides _get_full_queue_name method.
    """

    prefix_queue = ""

    async def _get_full_queue_name(self, queue_name, sufix=None):
        """Returns full_queue_name (with prefix & sufix, like "pending")"""
        full_queue_name = queue_name
        if self.prefix_queue:
            full_queue_name = f"{self.prefix_queue}:{full_queue_name}"
        if sufix:
            full_queue_name = f"{full_queue_name}:{sufix}"
        return full_queue_name


class RedisAsyncClientTaskCourier(
        FullQueueNameMixin, AbstractAsyncClientTaskCourier):
    """
    Class for the client side of task helpers using redis.

    Client side methods:
        - get_task_result - returns the result of the task, if it exists.
        - wait_for_task_result - waits for the result of the task to appear,
          and then returns it.
        - add_task_to_queue - adds one task to the queue for processing.
        - bulk_add_tasks_to_queue - adds many tasks to the queue for
          processing.
        - check_for_done - сhecks if the task has completed.
    """

    refresh_timeout = 0.1

    def __init__(self, aioredis_connection, **kwargs):
        self.aioredis_connection = aioredis_connection
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def _generate_task_id(self):
        if not hasattr(self, "_uuid1_is_safe"):
            self._uuid1_is_safe = uuid.uuid1().is_safe is uuid.SafeUUID.safe
        return uuid.uuid1() if self._uuid1_is_safe else uuid.uuid4()

    async def get_task_result(self, queue_name, task_id, delete_data=True):
        """Returns the result of the task, if it exists.
        Otherwise, raises exceptions.TaskResultDoesNotExist. If an error occurs
        during the execution of the task, returns exceptions.PerformTaskError.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        - delete_data - Whether to remove data from the queue after retrieving.
          default is True."""

        name = await self._get_full_queue_name(queue_name, "results:") + str(task_id)
        if delete_data:
            raw_data = await self.aioredis_connection.execute_command("GETDEL", name)
        else:
            raw_data = await self.aioredis_connection.get(name=name)
        if raw_data is None:
            raise exceptions.TaskResultDoesNotExist
        return pickle.loads(raw_data)

    async def wait_for_task_result(
            self, queue_name, task_id, delete_data=True, timeout=None):
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

        utc_start_time = datetime.datetime.utcnow()
        if isinstance(timeout, int) or isinstance(timeout, float):
            timeout = datetime.timedelta(seconds=timeout)
        first_iteration = True
        while first_iteration or not timeout or \
                utc_start_time + timeout > datetime.datetime.utcnow():
            try:
                first_iteration = False
                return await self.get_task_result(
                    queue_name=queue_name,
                    task_id=task_id,
                    delete_data=delete_data)
            except exceptions.TaskResultDoesNotExist:
                await asyncio.sleep(self.refresh_timeout)
        raise TimeoutError

    async def add_task_to_queue(self, queue_name, task_data):
        """Adds one task to the queue for processing. Returns task_id.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_data - task objects, what will be added to redis qeueue."""

        task_id = await self._generate_task_id()
        task = pickle.dumps((task_id, task_data))
        full_queue_name = await self._get_full_queue_name(
            queue_name=queue_name, sufix="pending")
        await self.aioredis_connection.rpush(full_queue_name, task)
        return task_id

    async def bulk_add_tasks_to_queue(self, queue_name, tasks_data):
        """Adds many tasks to the queue for processing.
        Returns a list of task_ids.
        Client side method.

        - queue_name - queue name, used in the add_task_to_queue method.
        - tasks_data - task objects, what will be added to redis qeueue."""

        tasks = list()
        task_ids = list()
        for task_data in tasks_data:
            task_id = await self._generate_task_id()
            task = pickle.dumps((task_id, task_data))
            task_ids.append(task_id)
            tasks.append(task)

        full_queue_name = await self._get_full_queue_name(
            queue_name=queue_name, sufix="pending")
        await self.aioredis_connection.rpush(full_queue_name, *tasks)
        return task_ids

    async def check_for_done(self, queue_name, task_id):
        """Сhecks if the task has completed.
        Returns True - if task is done (successful or unsuccessful),
        or False if there is no task result yet.

        - queue_name - queue name, used in the add_task_to_queue method.
        - task_id - id of the task that the add_task_to_queue method returned.
        """

        name = await self._get_full_queue_name(queue_name, "results:") + str(task_id)
        return bool(await self.aioredis_connection.exists(name))

