import traceback

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
    def __init__(self, exception: Exception | None = None,
                 exception_data: dict | None = None,
                 task: Task | tuple | None = None):
        self.exception = exception
        if exception:
            exception_data = self._get_exception_data(exception)
        self.exception_data = exception_data
        self.task = task

    def _get_exception_data(self, exception: Exception):
        return {
            "class_name": exception.__class__.__name__,
            "module_name": exception.__class__.__module__,
            "message": str(exception),
            "traceback": self._get_traceback_or_none(exception),
        }

    def _get_traceback_or_none(self, exception: Exception) -> str | None:
        traceback_str = None
        if hasattr(exception, "__traceback__") and exception.__traceback__:
            traceback_str = "".join(traceback.format_tb(exception.__traceback__))
        return traceback_str
