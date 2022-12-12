class DoesNotExistError(Exception):
    pass


class TaskDoesNotExist(DoesNotExistError):
    pass


class TaskResultDoesNotExist(DoesNotExistError):
    pass


class PerformTaskError:
    pass
