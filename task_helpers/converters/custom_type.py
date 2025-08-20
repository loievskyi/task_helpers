from typing import Any

from task_helpers.converters.stub import ConverterStub
from task_helpers.tasks import Task
from . import TaskTupleConverter
from .base import Converter
from .perform_task_error import PerformTaskErrorTupleConverter
from ..exceptions import PerformTaskError


class CustomTypeConverter(Converter[Any, tuple[bytes, Any]]):
    prefix_size = 1

    def __init__(self, perform_task_error_converter: PerformTaskErrorTupleConverter,
                 task_converter: TaskTupleConverter,
                 converter_stub: ConverterStub):
        self._default_prefix = b"\x00"
        self._type_prefix_map: dict[type, bytes] = dict()
        self._prefix_encoders_map: dict[bytes, Converter] = {
            self._default_prefix: converter_stub
        }

        self._add_converter(Task, task_converter)
        self._add_converter(PerformTaskError, perform_task_error_converter)

    def encode(self, source: Any) -> tuple[bytes, Any]:
        byte_prefix = self._type_prefix_map.get(
            type(source), self._default_prefix)
        converter = self._prefix_encoders_map[byte_prefix]
        encoded = converter.encode(source)
        return byte_prefix, encoded

    def decode(self, target: tuple[bytes, Any]) -> Any:
        byte_prefix, encoded = target
        converter = self._prefix_encoders_map[byte_prefix]
        return converter.decode(encoded)

    def _add_converter(self, source_type: type, converter: Converter):
        assert source_type not in self._type_prefix_map, "Type already exists"

        int_prefixes = [int.from_bytes(value) for value in self._prefix_encoders_map]
        new_prefix = max(int_prefixes) + 1
        new_prefix = new_prefix.to_bytes(self.prefix_size, "big")

        self._type_prefix_map[source_type] = new_prefix
        self._prefix_encoders_map[new_prefix] = converter
