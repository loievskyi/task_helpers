from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from .serializable import Serializable


@dataclass
class Task(Serializable):
    data: Any
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    def serialize(self):
        return self.id.bytes, self.data

    @classmethod
    def deserialize(cls, serialized_task):
        task_id_bytes, task_data = serialized_task
        task_id = uuid.UUID(bytes=task_id_bytes)
        return cls(id=task_id, data=task_data)


@dataclass
class ExtendedTask(Task):
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finish_at: float | None = None
    error: Exception | None = None
    retries: int = 0

    def serialize(self):
        task_as_tuple = (self.id.bytes, self.data, self.created_at, self.started_at,
                         self.finish_at, self.error, self.retries)
        return task_as_tuple

    @classmethod
    def deserialize(cls, serialized_task):
        (task_id, task_data, created_at, started_at,
         finish_at, error, retries) = serialized_task
        return cls(
            id=task_id,
            data=task_data,
            created_at=created_at,
            started_at=started_at,
            finish_at=finish_at,
            error=error,
            retries=retries
        )
