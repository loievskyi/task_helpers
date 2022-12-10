# Task helpers
## A package for creating task helpers.

## task_helpers module
The module allows you to work with tasks.
The idea is that it would be possible to create a task and send it for execution / processing somewhere (to the worker), without waiting for the result to be executed in the same block of code.
Or, for example, different clients (from different threads) can send many tasks for processing and each wait for its own result.

### TaskHelper methods (parent & inherited classes):
### Client side methods (ClientTaskHelper):
  - get_task_result - returns task retuls, if it exists;
  - wait_for_task_result - Waits for the task result to appear;
  - add_task_to_queue - adds a task to the queue for processing;
### Worker side methods (WorkerTaskHelper):
  - get_tasks - pops tasks from queue and returns it;
  - get_task - returns one task from queue;
  - wait_for_task - waits for task and returns it;
  - return_task_result - returns result to the client side.
### BaseClientWorkerTaskHelper:
  - all of the above
