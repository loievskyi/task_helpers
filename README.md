# Task helpers - a package for creating task helpers.
The package allows you to work with tasks.
The idea is that it would be possible to create a task and send it for execution / processing somewhere (to the worker), without waiting for the result to be executed in the same block of code.
Or, for example, different clients (from different threads) can send many tasks for processing and each wait for its own result.

## Usage example. Base worker
```bash
# Run redis (This can be done in many ways, not necessarily through docker):
docker run -p 6379:6379 redis
```

### Client side:
```python3
import redis

from task_helpers.couriers.redis import RedisClientTaskCourier

task_courier = RedisClientTaskCourier(redis_connection=redis.Redis())
QUEUE_NAME = "bulk_data_saving"


def to_save(task_data):
    # Adding a task to the queue.
    task_id = task_courier.add_task_to_queue(
        queue_name=QUEUE_NAME,
        task_data=task_data)

    # waiting for the task to complete in the worker.
    saved_object = task_courier.wait_for_task_result(
        queue_name=QUEUE_NAME,
        task_id=task_id)
    return saved_object


if __name__ == "__main__":
    # Many clients can add tasks to the queue at the same time.
    task_data = {
        "name": "tomato",
        "price": "12.45"
    }
    saved_object = to_save(task_data=task_data)
    print(saved_object)
    # {'name': 'tomato', 'price': '12.45', 'id': UUID('...'), 'status': 'active')}

```

### Worker side:
```python3
import uuid
import redis

from task_helpers.couriers.redis import RedisWorkerTaskCourier
from task_helpers.workers.base import BaseWorker

task_courier = RedisWorkerTaskCourier(redis_connection=redis.Redis())
QUEUE_NAME = "bulk_data_saving"


class BulkSaveWorker(BaseWorker):
    queue_name = QUEUE_NAME

    def bulk_saving_plug(self, tasks):
        for task_id, task_data in tasks:
            task_data["id"] = uuid.uuid4()
            task_data["status"] = "active"
        return tasks

    def perform_tasks(self, tasks):
        tasks = self.bulk_saving_plug(tasks)
        # Bulk saving data_dicts (it's faster than saving 1 at a time.)

        print(f"saved {len(tasks)} objects.")
        # saved 1 objects.

        return tasks


if __name__ == "__main__":
    worker = BulkSaveWorker(task_courier=task_courier)
    worker.perform(total_iterations=500)
    # the worker will complete its work after 500 iterations
    # (in the future functionality it is necessary to prevent memory leaks)

```

## Installation
```bash
pip install task_helpers
```

## The couriers module
the couriers module is responsible for sending tasks from the worker to the client and back, as well as checking the execution status.

### Client side methods (ClientTaskCourier):
- get_task_result - returns the result of the task, if it exists.
- wait_for_task_result - waits for the result of the task to appear, and then returns it.
- add_task_to_queue - adds one task to the queue for processing.
- bulk_add_tasks_to_queue - adds many tasks to the queue for processing.
- check_for_done - сhecks if the task has completed.

### Worker side methods (WorkerTaskCourier):
- get_task - pops one task from the queue and returns it.
- bulk_get_tasks - pops many tasks from the queue and returns them.
- wait_for_task - Waits for a task to appear, pops it from the queue, and returns it.
- return_task_result - returns the result of the processing of the task to the client side.
- bulk_return_task_results - returns the results of processing multiple tasks to the client side.

### ClientWorkerTaskCourier:
- all of the above

## The workers module
The workers module is intended for executing and processing tasks.

### BaseWorker
A worker that can process many tasks in one iteration. (This can be useful if task_data are objects on which some operations can be done in bulk)

### BaseWorker methods:
- wait_for_tasks - waits for tasks in the queue, pops and returns them;
- perform_tasks - method for processing tasks. Should return a list of tasks.
- perform_single_task - abstract method for processing one task. Should return the result of the task. Not used if the "perform_tasks" method is overridden.
- return_task_results - method method for sending task results to the clients.
- perform - the main method that starts the task worker. total_iterations argument are required (how many processing iterations the worker should do.)

### ClassicWorker
Сlassic worker, where the task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Arguments "args" and "kwargs" are optional.

### ClassicWorker methods:
- perform_single_task - method for processing one task. Should return the result of the task. Not used if the "perform_tasks" method is overridden.
task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Calls a function with args "args" and kwargs "kwargs", unpacking them, and returns the execution result.
Arguments "args" and "kwargs" are optional.
