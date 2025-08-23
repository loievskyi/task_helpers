import uuid
from typing import Any

from task_helpers.serializers import TaskSerializer, CustomTypeSerializer
from task_helpers.tasks import Task
from .mixins import QueueNameMixin
from .. import exceptions

__all__ = [
    "ClientSideCourier",
    "WorkerSideCourier",
    "Courier",
]

from task_helpers.backends.sync.base import Backend


class ClientSideCourier(QueueNameMixin):
    """
    Class for the client side of task helpers.

    Client side methods:
        - get_task_result - returns the result of the task, if it exists.
        - wait_for_task_result - waits for the result of the task to appear,
          and then returns it.
        - add_task_to_queue - adds one task to the queue for processing.
        - bulk_add_tasks_to_queue - adds many tasks to the queue for
          processing.
        - check_for_done - checks if the task has completed.
    """

    def __init__(self, task_serializer: TaskSerializer,
                 task_result_serializer: CustomTypeSerializer,
                 backend: Backend, **kwargs) -> None:
        self._task_serializer = task_serializer
        self._task_result_serializer = task_result_serializer
        self._backend = backend

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_task_to_queue(self, queue_name: str, task_data: Any) -> uuid.UUID:
        queue_name = self._build_queue_name(queue_name, suffix="pending")
        task = self._generate_task(task_data)
        serialized_task = self._task_serializer.serialize(task)
        self._backend.add_to_queue(queue_name, serialized_task)
        return task.id

    def bulk_add_tasks_to_queue(self, queue_name: str, tasks_data: list) -> list[uuid.UUID]:
        if not tasks_data:
            return []

        queue_name = self._build_queue_name(queue_name, suffix="pending")
        tasks = [self._generate_task(task_data) for task_data in tasks_data]
        serialized_tasks = [self._task_serializer.serialize(task) for task in tasks]
        self._backend.bulk_add_to_queue(queue_name, serialized_tasks)
        return [task.id for task in tasks]

    def get_task_result(self, queue_name: str, task_id: uuid.UUID, delete_data: bool = True) -> Any:
        queue_name = self._build_queue_name(queue_name, f"results:{str(task_id)}")
        raw_data = self._backend.pop_or_requeue(queue_name, delete_data=delete_data,
                                                error_class=exceptions.TaskResultDoesNotExist)
        return self._task_result_serializer.deserialize(raw_data)

    def wait_for_task_result(self, queue_name: str, task_id: uuid.UUID,
                             delete_data: bool = True, timeout_seconds: int | None = None) -> Any:
        queue_name = self._build_queue_name(queue_name, f"results:{str(task_id)}")
        raw_data = self._backend.pop_or_requeue_blocking(queue_name, delete_data=delete_data,
                                                         timeout_seconds=timeout_seconds)
        return self._task_result_serializer.deserialize(raw_data)

    def check_for_done(self, queue_name: str, task_id: uuid.UUID) -> bool:
        queue_name = self._build_queue_name(queue_name, f"results:{str(task_id)}")
        return self._backend.exists(queue_name)

    def _generate_task(self, task_data: Any) -> Task:
        return Task(
            id=self._generate_task_id(),
            data=task_data)

    def _generate_task_id(self) -> uuid.UUID:
        if not hasattr(self, "_uuid1_is_safe"):
            self._uuid1_is_safe = uuid.uuid1().is_safe is uuid.SafeUUID.safe
        return uuid.uuid1() if self._uuid1_is_safe else uuid.uuid4()


class WorkerSideCourier(QueueNameMixin):
    """
    Class for the worker side of task helpers.

    Worker side methods:
        - get_task - pops one task from the queue and returns it.
        - bulk_get_tasks - pops many tasks from the queue and returns them.
        - wait_for_task - waits for a task to appear, pops it from the queue,
          and returns it.
        - bulk_wait_for_tasks - waits for tasks in the queue, pops and returns
          them.
        - return_task_result - returns the result of the processing of the task
          to the client side.
        - bulk_return_tasks_results - returns the results of processing
          multiple tasks to the client side.
    """

    result_timeout_seconds: int | None = 600  # Set None to keep task_result permanently.

    def __init__(self, task_serializer: TaskSerializer,
                 task_result_serializer: CustomTypeSerializer,
                 backend: Backend, **kwargs) -> None:
        self._task_serializer = task_serializer
        self._task_result_serializer = task_result_serializer
        self._backend = backend

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_task(self, queue_name: str) -> Task:
        queue_name = self._build_queue_name(queue_name, "pending")
        serialized = self._backend.pop_from_queue(queue_name, error_class=exceptions.TaskDoesNotExist)
        return self._task_serializer.deserialize(serialized)

    def bulk_get_tasks(self, queue_name: str, max_count: int) -> list[Task]:
        queue_name = self._build_queue_name(queue_name, "pending")
        serialized_tasks = self._backend.bulk_pop_from_queue(queue_name, max_count)
        return [self._task_serializer.deserialize(task) for task in serialized_tasks]

    def wait_for_task(self, queue_name: str, timeout_seconds: int | None = None) -> Task:
        queue_name = self._build_queue_name(queue_name, "pending")
        serialized = self._backend.pop_from_queue_blocking(queue_name, timeout_seconds=timeout_seconds)
        return self._task_serializer.deserialize(serialized)

    def bulk_wait_for_tasks(self, queue_name: str, max_count: int,
                            timeout_seconds: int | None = None) -> list[Task]:
        tasks = self.bulk_get_tasks(queue_name=queue_name, max_count=max_count)
        if not tasks:
            return [self.wait_for_task(queue_name=queue_name, timeout_seconds=timeout_seconds)]
        return tasks

    def return_task_result(self, queue_name: str, task: Task) -> None:
        queue_name = self._build_queue_name(queue_name, suffix=f"results:{str(task.id)}")
        serialized = self._task_result_serializer.serialize(task.result)
        with self._backend.pipeline() as pipeline:
            pipeline.add_to_queue(queue_name, serialized)
            if self.result_timeout_seconds:
                pipeline.expire(queue_name, self.result_timeout_seconds)

    def bulk_return_tasks_results(self, queue_name: str, tasks: list[Task]) -> None:
        keys_and_data = [
            (self._build_queue_name(queue_name, f"results:{str(task.id)}"),
             self._task_result_serializer.serialize(task.result))
            for task in tasks
        ]

        with self._backend.pipeline() as pipeline:
            for key, data in keys_and_data:
                pipeline.add_to_queue(key, data)
                if self.result_timeout_seconds:
                    pipeline.expire(key, self.result_timeout_seconds)


class Courier(ClientSideCourier, WorkerSideCourier):
    """
    Class for the client and worker sides of task helpers.

    Client side methods:
        - get_task_result - returns the result of the task, if it exists.
        - wait_for_task_result - waits for the result of the task to appear,
          and then returns it.
        - add_task_to_queue - adds one task to the queue for processing.
        - bulk_add_tasks_to_queue - adds many tasks to the queue for
          processing.
        - check_for_done - checks if the task has completed.

    Worker side methods:
        - get_task - pops one task from the queue and returns it.
        - bulk_get_tasks - pops many tasks from the queue and returns them.
        - wait_for_task - waits for a task to appear, pops it from the queue,
          and returns it.
        - bulk_wait_for_tasks - waits for tasks in the queue, pops and returns
          them.
        - return_task_result - returns the result of the processing of the task
          to the client side.
        - bulk_return_tasks_results - returns the results of processing
          multiple tasks to the client side.
    """
