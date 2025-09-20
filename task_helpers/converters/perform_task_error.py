from task_helpers.converters import TaskTupleConverter
from .base import Converter
from ..exceptions import PerformTaskError


class PerformTaskErrorTupleConverter(Converter[PerformTaskError, tuple]):
    def __init__(self, task_converter: TaskTupleConverter):
        self._task_converter = task_converter

    def encode(self, source: PerformTaskError) -> tuple:
        encoded_task = self._task_converter.encode(source.task) if source.task else None
        encoded_exception_data = (
            source.exception_data["class_name"],
            source.exception_data["module_name"],
            source.exception_data["message"],
            source.exception_data["traceback"],
        )
        return encoded_task, encoded_exception_data

    def decode(self, target: tuple) -> PerformTaskError:
        encoded_task, encoded_exception_data = target
        task = self._task_converter.decode(encoded_task) if encoded_task else None
        return PerformTaskError(
            task=task,
            exception_data={
                "class_name": encoded_exception_data[0],
                "module_name": encoded_exception_data[1],
                "message": encoded_exception_data[2],
                "traceback": encoded_exception_data[3],
            })
