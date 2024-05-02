import time
import multiprocessing
import random
import logging
import queue
import threading
import gc
import asyncio
import inspect


class BaseWorkerHandler:
    count_workers = 2
    iterations_to_restart = 100
    iterations_to_restart_jitter = 20
    worker_class = None
    task_courier_class = None

    @property
    def process_name(self):
        if self.worker_class:
            return f"taskhelpers.{self.worker_class.__name__}." \
                f"{self.worker_class.queue_name}"
        return "taskhelpers.worker"

    def __init__(self, worker_init_kwargs=None, **kwargs):
        self.threads = queue.Queue()
        self.worker_init_kwargs = worker_init_kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def new_process_starter(self):
        while True:
            try:
                process = multiprocessing.Process(
                    target=self.perform_worker,
                    name=self.process_name)
                process.daemon = True
                process.start()
                process.join()
                del process
                gc.collect()
            except Exception as ex:
                logging.exception(
                    f"An error has occured on {self.__class__.__name__}."
                    f"new_process_starter: {ex}")
                time.sleep(1)

    def create_worker_instance(self):
        raise NotImplementedError

    def perform_worker(self):
        try:
            iterations_to_restart = self.iterations_to_restart + \
                random.randint(0, self.iterations_to_restart_jitter)
            worker = self.create_worker_instance()
            if inspect.iscoroutinefunction(worker.perform):
                asyncio.run(
                    worker.perform(total_iterations=iterations_to_restart)
                )
            else:
                worker.perform(total_iterations=iterations_to_restart)
        except Exception as ex:
            time.sleep(0.1)
            logging.exception(
                f"An error has occured on {self.__class__.__name__}"
                f".perform_worker: {ex}")

    def perform(self):
        for num in range(1, self.count_workers+1):
            try:
                thread = threading.Thread(target=self.new_process_starter)
                thread.start()
                self.threads.put(thread)
            except Exception as ex:
                logging.exception(
                    f"An error has occured on {self.__class__.__name__}"
                    f".perform: {ex}")
        self.threads.join()
