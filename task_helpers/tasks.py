import uuid
import datetime

from task_helpers import exceptions


class Task:
    """
    Base class for tasks.
    """

    def __init__(
            self, queue_name, id=None, input_data=None, result=None,
            function=None, function_args=None, function_kwargs=None):
        """
        Class initialization. All argumengs are optional.
        """
        assert input_data is not None or function is not None, \
            "\"input_data\" or \"function\" arguments must be specified"

        self.id = id or uuid.uuid4()
        self.function = function
        self.function_args = function_args or tuple()
        self.function_kwargs = function_kwargs or dict()
        self.input_data = input_data
        self.result = result
        self.started_at = datetime.datetime.utcnow()

    def makr_as_done(self, task_result):
        """
        Marks the task as done.
        """
        self.result = task_result
        self.finished_at = datetime.datetime.utcnow()

    def mark_as_error(self, error_details):
        """
        Marks the task as error.
        """
        self.result = exceptions.PerformTaskError(error_details)
        self.finished_at = datetime.datetime.utcnow()

    def __str__(self):
        return f"task {self.id}"
