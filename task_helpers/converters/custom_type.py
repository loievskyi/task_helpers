from typing import Any

from task_helpers.converters.slug import ConverterSlug
from .base import Converter
from .perform_task_error_tuple import PerformTaskErrorTupleConverter
from ..exceptions import PerformTaskError


class CustomTypeConverter(Converter[Any, tuple[bytes, Any]]):
    prefix_size = 1

    def __init__(self, perform_task_error_converter: PerformTaskErrorTupleConverter,
                 converter_slug: ConverterSlug):
        self._perform_task_error_converter = perform_task_error_converter
        self._converter_slug = converter_slug

        self._type_prefix_map = {
            PerformTaskError: b"\x01",
            "default": b"\x00",
        }

        self._prefix_encoders_map = {
            b"\x01": self._perform_task_error_converter,
            b"\x00": self._converter_slug,
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
