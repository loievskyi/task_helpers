class BaseClientTaskHelper(object):
    """
    Base class for the client side of task helpers.

    The inherited class should provide the ability to:
    - Client side:
        - to add task objects (not only as functions) to the queue;
        - wait for the result;
    """

    def get_task_result(self, *args, **kwargs):
        """Waits for the task result to appear, and then returns it.
        Client side method."""
        raise NotImplementedError

    def add_task_to_queue(self, queue_name, task_data, sufix="pending"):
        """Put the task in the queue for processing.
        Client side method."""
        raise NotImplementedError


class BaseWorkerTaskHelper(object):
    """
    Base class for the worker side of task helpers.

    The inherited class should provide the ability to:
    - Worker side:
        - take the one task from the queue;
        - take many tasks from queue (more productive than taking
          one task at a time from the queue);
        - return the task response to the client
    """

    def get_tasks(self, *args, **kwargs):
        """Pops tasks from queue and returns it. The number of task which
        depends on max_count and the number of elements in the queue.
        Worker side method."""
        raise NotImplementedError

    def get_task(self, *args, **kwargs):
        """Returns single task from the queue.
        Worker side method."""
        raise NotImplementedError

    def return_task_result(self, queue_name, task_id, task_data):
        """Return the result of processing the task to the client.
        Worker side method."""
        raise NotImplementedError


class BaseClientWorkerTaskHelper(BaseWorkerTaskHelper, BaseClientTaskHelper):
    """
    Base class for the client and worker sides of task helpers.

    The inherited class should provide the ability to:
    - Client side:
        - to add task objects (not only as functions) to the queue;
        - wait for the result;
    - Worker side:
        - take the task from the queue;
        - return the task response to the client
    """

    pass
