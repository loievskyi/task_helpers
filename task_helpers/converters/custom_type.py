from typing import Any

from task_helpers.converters.stub import ConverterStub
from . import TaskTupleConverter
from .base import Converter
from .perform_task_error import PerformTaskErrorTupleConverter
from ..exceptions import PerformTaskError


class CustomTypeConverter(Converter[Any, tuple[bytes, Any]]):
    prefix_size = 1

    def __init__(self, perform_task_error_converter: PerformTaskErrorTupleConverter,
                 task_converter: TaskTupleConverter,
                 converter_stub: ConverterStub):
        self._perform_task_error_converter = perform_task_error_converter
        self._task_converter = task_converter
        self._converter_stub = converter_stub

        from task_helpers.tasks import Task
        self._type_prefix_map = {
            "default": b"\x00",
            PerformTaskError: b"\x01",
            Task: b"\x02",
        }

        self._prefix_encoders_map = {
            b"\x00": self._converter_stub,
            b"\x01": self._perform_task_error_converter,
            b"\x02": self._task_converter,
        }

    def encode(self, source: Any) -> tuple[bytes, Any]:
        byte_prefix = self._type_prefix_map.get(type(source), b"\x00")
        converter = self._prefix_encoders_map[byte_prefix]
        encoded = converter.encode(source)
        return byte_prefix, encoded

    def decode(self, target: tuple[bytes, Any]) -> Any:
        byte_prefix, encoded = target
        converter = self._prefix_encoders_map[byte_prefix]
        return converter.decode(encoded)
