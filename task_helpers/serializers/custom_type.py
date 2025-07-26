from typing import Any

from task_helpers.compressors import Compressor
from task_helpers.converters import BytesConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from .base import Serializer


class CustomTypeSerializer(Serializer[Any, bytes]):
    """Main class that combines all serialization stages"""

    def __init__(
            self,
            custom_type_converter: CustomTypeConverter,
            bytes_converter: BytesConverter,
            compressor: Compressor,
    ):
        self._custom_type_converter = custom_type_converter
        self._bytes_converter = bytes_converter
        self._compressor = compressor
        self._prefix_size = self._custom_type_converter.prefix_size

    def serialize(self, source: Any) -> bytes:
        """Serialize an object to compressed bytes"""

        type_prefix, partially_serialized = self._custom_type_converter.encode(source)
        partially_serialized = self._bytes_converter.encode(partially_serialized)
        partially_serialized = self._compressor.compress(partially_serialized)

        return type_prefix + partially_serialized

    def deserialize(self, serialized: bytes) -> Any:
        """Deserialize an object from compressed bytes"""

        type_prefix = self._get_prefix(serialized, self._prefix_size)
        data = self._get_data(serialized, self._prefix_size)
        data = self._compressor.decompress(data)
        data = self._bytes_converter.decode(data)
        return self._custom_type_converter.decode((type_prefix, data))

    def _get_prefix(self, serialized: bytes, prefix_size: int) -> bytes:
        return serialized[:prefix_size]

    def _get_data(self, serialized: bytes, prefix_size: int) -> bytes:
        return serialized[prefix_size:]
