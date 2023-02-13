# Task helpers - a package for creating task helpers.

[![build](https://github.com/loievskyi/task_helpers/actions/workflows/build.yml/badge.svg?branch=master)](https://github.com/loievskyi/task_helpers/actions/workflows/build.yml)
[![pypi](https://img.shields.io/pypi/v/task_helpers.svg)](https://pypi.org/project/task-helpers/)
[![coverage](https://img.shields.io/codecov/c/github/loievskyi/task_helpers/master.svg)](https://codecov.io/github/loievskyi/task_helpers?branch=master)

The package allows you to work with tasks.
The idea is that it would be possible to create a task and send it for execution / processing somewhere (to the worker), without waiting for the result to be executed in the same block of code.
Or, for example, different clients (from different threads) can send many tasks for processing and each wait for its own result.

## Usage example. BaseWorker
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
    max_tasks_per_iteration = 500

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

### BaseWorker & BaseAsyncWorker
A worker that can process many tasks in one iteration. (This can be useful if task_data are objects on which some operations can be done in bulk)
#### On BaseAsyncWorker.max_tasks_per_iteration default value is 1. If you want to process many tasks (similar to a BaseWorker), change the value of this field in the inherited class.

### BaseWorker methods:
- wait_for_tasks - waits for tasks in the queue, pops and returns them;
- perform_tasks - method for processing tasks. Should return a list of tasks.
- perform_single_task - abstract method for processing one task. Should return the result of the task. Not used if the "perform_tasks" method is overridden.
- return_task_results - method for sending task results to the clients.
- destroy - method for destroy objects after performing (requests.Session().close, for example)
- perform - the main method that starts the task worker. total_iterations argument are required (how many processing iterations the worker should do.)

### BaseAsyncWorker methods:
- async_init - aync init method for initialization async objects (aiohttp.ClientSession, for example).
- async_destroy - async destroy method for destroy async objects (aiohttp.ClientSession().close, for example).

The other methods are similar to the BaseWorker methods, but they are asynchronous and have slightly different logic inside:
- New task iteration start after starting previous "perform_tasks" method
(Not after its completion, as it was in the synchronous BaseWorker).

### ClassicWorker & ClassicAsyncWorker
Сlassic worker, where the task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Arguments "args" and "kwargs" are optional.

### ClassicWorker methods:
- perform_single_task - method for processing one task. Should return the result of the task. Not used if the "perform_tasks" method is overridden.
task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Calls a function with args "args" and kwargs "kwargs", unpacking them, and returns the execution result.
Arguments "args" and "kwargs" are optional.

### ClassicAsyncWorker methods:
- perform_single_task - method for processing one task. Should return the result of the task. Not used if the "perform_tasks" method is overridden.
task is a tuple: (task_id, task_data).
task_data is a dictionary with keys "function", "args" and "kwargs".
Calls a function asynchronously, with args "args" and kwargs "kwargs", unpacking them, and returns the execution result.
Arguments "args" and "kwargs" are optional. If the function is not asynchronous, will be called in "loop.run_in_executor" method.

## One more usage example. BaseAsyncWorker
```bash
# Run redis (This can be done in many ways, not necessarily through docker):
docker run -p 6379:6379 redis
```

### Client side:
```python3
import time
import redis
import requests

from task_helpers.couriers.redis import RedisClientTaskCourier

task_courier = RedisClientTaskCourier(redis_connection=redis.Redis())
QUEUE_NAME = "async_data_downloading"


def download_with_async_worker(urls: list):
    # Adding a task to the queue.
    task_ids = task_courier.bulk_add_tasks_to_queue(
        queue_name=QUEUE_NAME,
        tasks_data=urls)

    # waiting for the task to complete in the worker.
    for task_id in task_ids:
        downloaded_data = task_courier.wait_for_task_result(
            queue_name=QUEUE_NAME,
            task_id=task_id)
        if isinstance(downloaded_data, dict):
            yield downloaded_data["name"]
        else:
            yield downloaded_data.exception


def download_with_sync_session(urls: list):
    with requests.Session() as session:
        for url in urls:
            yield session.get(url)


if __name__ == "__main__":
    # Many clients can add tasks to the queue at the same time.
    urls = [f"https://pokeapi.co/api/v2/pokemon/{num}/" for num in range(100)]

    # async worker
    # Цaiting for the worker to start so that the execution time is correct.
    list(download_with_async_worker(urls=urls[:1]))

    before_time = time.perf_counter()
    names = list(download_with_async_worker(urls=urls))
    after_time = time.perf_counter()
    print(f"names: {names} \n")
    print(f"Time for downloading {len(names)} urls with async worker: "
          f"{after_time-before_time} sec.")

    # sync session
    before_time = time.perf_counter()
    names = list(download_with_sync_session(urls=urls))
    after_time = time.perf_counter()
    print(f"Time for downloading {len(names)} urls with requests.session: "
          f"{after_time-before_time} sec.")

```

### Worker side:
```python3
import redis
import asyncio
import aiohttp

from task_helpers.couriers.redis import RedisWorkerTaskCourier
from task_helpers.workers.base_async import BaseAsyncWorker

task_courier = RedisWorkerTaskCourier(redis_connection=redis.Redis())
QUEUE_NAME = "async_data_downloading"


class AsyncDownloadingWorker(BaseAsyncWorker):
    queue_name = QUEUE_NAME
    empty_queue_sleep_time = 0.01

    async def async_init(self):
        self.async_session = aiohttp.ClientSession()

    async def async_destroy(self):
        await self.async_session.close()

    async def download(self, url):
        print(f"Start downloading {url}")
        async with self.async_session.get(url) as response:
            if response.status == 200:
                response_json = await response.json()
                print(f"Downloaded. Status: {response.status}. Url: {url}")
                return response_json
            elif response.status == 404:
                print(f"Predownloaded. Status: {response.status}. Url: {url}")
                raise Exception(404)
            else:
                await asyncio.sleep(0.1)
                return await self.download(url)

    async def perform_single_task(self, task):
        task_id, task_data = task
        return await self.download(url=task_data)


if __name__ == "__main__":
    worker = AsyncDownloadingWorker(task_courier=task_courier)
    asyncio.run(
        worker.perform(total_iterations=10_000)
    )

```
