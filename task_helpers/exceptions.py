class DoesNotExistError(Exception):
    pass


class TaskDoesNotExist(DoesNotExistError):
    pass


class TaskResultDoesNotExist(DoesNotExistError):
    pass


class PerformTaskError(Exception):
    def __init__(self, exception=None, error_data=None, task=None):
        self.task = task
        self.exception = exception
        self.error_data = error_data
