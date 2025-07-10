import time
from abc import ABC, abstractmethod

from task_helpers.couriers import WorkerSideCourier
from task_helpers.exceptions import PerformTaskError
from task_helpers.tasks import Task


class Worker(ABC):
    queue_name: str
    count_iterations: int = 10_000
    max_tasks_per_iteration: int = 10
    iteration_delay_seconds: float | int = 0
    needs_result_returning: bool = True

    def __init__(self, courier: WorkerSideCourier):
        self._courier = courier

    def perform(self, count_iterations: int = count_iterations) -> None:
        for _ in range(count_iterations):
            tasks = self._wait_for_tasks()
            self._safe_perform_tasks(tasks)
            if self.needs_result_returning:
                self._courier.bulk_return_tasks_results(
                    queue_name=self.queue_name,
                    tasks=tasks)
            time.sleep(self.iteration_delay_seconds)

    def _wait_for_tasks(self) -> list[Task]:
        tasks = self._courier.bulk_wait_for_tasks(
            queue_name=self.queue_name,
            max_count=self.max_tasks_per_iteration)
        return tasks

    def _safe_perform_tasks(self, tasks: list[Task]) -> None:
        try:
            self._perform_tasks(tasks)
        except Exception as ex:
            for task in tasks:
                task.result = PerformTaskError(task=task, exception=ex)

    def _perform_tasks(self, tasks: list[Task]) -> None:
        for task in tasks:
            self._safe_perform_single_task(task)

    def _safe_perform_single_task(self, task: Task) -> None:
        try:
            self._perform_single_task(task)
        except Exception as ex:
            task.result = PerformTaskError(task=task, exception=ex)

    @abstractmethod
    def _perform_single_task(self, task: Task) -> None:
        ...
