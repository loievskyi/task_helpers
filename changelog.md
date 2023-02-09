# [1.2.0] - 2023-02-xx
- Added async workers:
  - AbstractAsyncWorker
  - BaseAsyncWorker
  - ClassicAsyncWorker

# [1.1.1] - 2023-01-23
- Readme changes
- Changes on docs
- fixes on courier: now courier.bulk_return_task_results tasks arg is list of tuples [(task_id, task_result), ...]

# [1.1.0] - 2023-01-23
- New logic for _generate_task_id method.
- ClientTaskCourier.added bulk_add_tasks_to_queue method & tests for it.
- WorkerTaskCourier.added bulk_return_task_results method & tests for it.
- Renamed WorkerTaskCourier.get_tasks => WorkerTaskCourier.bulk_get_tasks.
- Performanse & naming fixes.
- Readme fixes.

# [1.0.5] - missed
- Performanse & naming fixes.

# [1.0.4] - missed
- WorkerTaskCourier.added bulk_return_task_results method & tests for it.
- Renamed WorkerTaskCourier.get_tasks => WorkerTaskCourier.bulk_get_tasks.

# [1.0.3] - missed
- ClientTaskCourier.added bulk_add_tasks_to_queue method & tests for it.

# [1.0.2] - missed
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
