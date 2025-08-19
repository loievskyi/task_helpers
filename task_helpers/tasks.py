from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    data: Any
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    result: Any = None


# reserve for the future
@dataclass
class ExtendedTask(Task):
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finish_at: float | None = None
    error: Exception | None = None
    retries: int = 0
