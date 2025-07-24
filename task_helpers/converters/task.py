import uuid
from typing import Any

from .base import Converter
from task_helpers.tasks import Task


class TaskTupleConverter(Converter[Task, tuple]):
    def __init__(self, task_data_converter: Converter):
        self._task_data_converter = task_data_converter

    def encode(self, source: Task) -> tuple[bytes, Any]:
        encoded_id = source.id.bytes
        encoded_data = self._task_data_converter.encode(source.data)
        return encoded_id, encoded_data

    def decode(self, target: tuple[bytes, Any]) -> Task:
        task_id = uuid.UUID(bytes=target[0])
        task_data = self._task_data_converter.decode(target[1])
        return Task(id=task_id, data=task_data)
