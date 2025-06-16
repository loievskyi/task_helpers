import uuid
from typing import Any

from .base import Converter
from task_helpers.tasks.task import Task


class TaskTupleConverter(Converter[Task, tuple]):
    def encode(self, source: Task) -> tuple[uuid.UUID, Any]:
        return source.id, source.data

    def decode(self, target: tuple[bytes, Any]) -> Task:
        data = target[1]
        task_id = uuid.UUID(bytes=target[0])
        return Task(id=task_id, data=data)
