# Task helpers - a package for creating task helpers.
The package allows you to work with tasks.
The idea is that it would be possible to create a task and send it for execution / processing somewhere (to the worker), without waiting for the result to be executed in the same block of code.
Or, for example, different clients (from different threads) can send many tasks for processing and each wait for its own result.

### SOLID
An abstract class describes the methods that derived classes must have. The input and output data types are also described.

## The couriers module
the couriers module is responsible for sending tasks from the worker to the client and back, as well as checking the execution status.

### Client side methods (ClientTaskCourier):
- get_task_result - returns task retuls, if it exists.
- wait_for_task_result - Waits for the task result to appear.
- add_task_to_queue - adds a task to the queue for processing;

### Worker side methods (WorkerTaskCourier):
- get_tasks - pops tasks from queue and returns it.
- get_task - returns one task from queue.
- wait_for_task - waits for task and returns it.
- return_task_result - returns result to the client side.

### ClientWorkerTaskCourier:
- all of the above

## The workers module
The workers module is intended for executing and processing tasks.

### BaseWorker
A worker that can process many tasks in one iteration. (This can be useful if task_data are objects on which some operations can be done in bulk)

### BaseWorker methods:
- wait_for_tasks - waits for tasks in the queue, pops and returns them;
- perform_tasks - abstract method for processing tasks. Should return a list of tasks.
- return_task_results - method method for sending task results to the clients.
- perform - the main method that starts the task worker. total_iterations argument are required (how many processing iterations the worker should do.)

### ClassicWorker
Сlassic worker, where the task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Arguments "args" and "kwargs" are optional.

### ClassicWorker methods:
- perform_tasks - Method for processing tasks. Returns a list of tasks.
task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Calls a function with args "args" and kwargs "kwargs", unpacking them, and returns the execution result.
Arguments "args" and "kwargs" are optional.
