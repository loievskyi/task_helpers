# [1.4.1] - 2024-02-24
- Asynchronous couriers has been added:
  - AbstractAsyncClientTaskCourier
  - AbstractAsyncWorkerTaskCourier
  - AbstractAsyncClientWorkerTaskCourier
  - RedisAsyncClientTaskCourier
  - RedisAsyncWorkerTaskCourier
  - AbstractAsyncClientWorkerTaskCourier

# [1.4.0] - 2023-12-21 - withdrawn
- Asynchronous couriers has been added and workers has been changed.

# [1.3.2] - 2023-02-23
- Changes on redis courier init method: added **kwargs (to assign them to an instance).


# [1.3.1] - 2023-02-13
- Added async workers & tests for themt:
  - AbstractAsyncWorker
  - BaseAsyncWorker
  - ClassicAsyncWorker
- Added async_init & async_destroy methods for async workers.
- Added destroy method for sync workers.

# [1.3.0] - 2023-02-11 - withdrawn

# [1.2.1] - 2023-02-11
- Readme fixes.

# [1.2.0] - 2023-02-11
- Added bulk operations for TaskCourier's:
  - ClientTaskCourier - added bulk_add_tasks_to_queue method & tests for it.
  - WorkerTaskCourier - added bulk_return_task_results method & tests for it.
  - Renamed WorkerTaskCourier.get_tasks => WorkerTaskCourier.bulk_get_tasks.
- Fixes on courier: now courier.bulk_return_task_results "tasks" arg is list of tuples [(task_id, task_result), ...].
- Performanse improvements.
- Changes on docs & readme.

# [1.1.0] - 2023-01-23 - withdrawn
- New logic for _generate_task_id method.

# [1.0.1] - 2023-01-05
Readme fixes.

# [1.0.0] - 2022-12-01
Release.
- Added Task couriers
  - ClientTaskCourier
    - get_task_result - returns task retuls, if it exists.
    - wait_for_task_result - Waits for the task result to appear.
    - add_task_to_queue - adds a task to the queue for processing.
    - check_for_done - checks if the task has completed.
  - WorkerTaskCourier
    - get_tasks - pops many tasks from queue and returns it.
    - get_task - pops one task from queue and returns it.
    - wait_for_task - waits for task and returns it.
    - return_task_result - returns result to the client side.
- BaseWorker
  - wait_for_tasks - waits for tasks in the queue, pops and returns them.
  - perform_tasks - abstract method for processing tasks. Should return a list of tasks.
  - return_task_results - method method for sending task results to the clients.
  - perform - the main method that starts the task worker. total_iterations argument are required (how many processing iterations the worker should do).
- ClassicWorker
  - perform_tasks - Method for processing tasks. Returns a list of tasks.
  task is a tuple: (task_id, task_data).
  task_data is a dictionary with keys "function", "args" and "kwargs".
  Calls a function with args "args" and kwargs "kwargs", unpacking them, and returns the execution result.
  Arguments "args" and "kwargs" are optional.
