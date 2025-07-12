from typing import Any, Type

from task_helpers.tasks import Task


class TaskHelperError(Exception):
    pass


class DoesNotExistError(TaskHelperError):
    pass


class TaskDoesNotExist(DoesNotExistError):
    pass


class TaskResultDoesNotExist(DoesNotExistError):
    pass


class PerformTaskError(TaskHelperError):
    def __init__(self, exception: Exception | Type[Exception] = None,
                 error_data: Any = None,
                 task: Task | tuple | None = None):
        self.exception = exception
        self.error_data = error_data
        self.task = task
