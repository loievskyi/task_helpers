class DoesNotExistError(Exception):
    pass


class TaskDoesNotExist(DoesNotExistError):
    pass


class TaskResultDoesNotExist(DoesNotExistError):
    pass


class PerformTaskError(Exception):
    def __init__(self, error_data=None):
        self.error_data = error_data
