from typing import Any

from task_helpers.compressors import Compressor
from task_helpers.converters import BytesConverter
from .base import Serializer


class TaskResultSerializer(Serializer[Any, bytes]):
    """Main class that combines all serialization stages"""

    def __init__(
            self,
            bytes_converter: BytesConverter,
            compressor: Compressor
    ):
        self._bytes_converter = bytes_converter
        self._compressor = compressor

    def serialize(self, task_result: Any) -> bytes:
        """
        Serialize an object to compressed bytes

        The process includes:
        1. Converting an object to bytes
        2. Compressing bytes
        """
        bytes_data = self._bytes_converter.encode(task_result)
        compressed_data = self._compressor.compress(bytes_data)
        return compressed_data

    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize an object from compressed bytes

        The process includes:
        1. Decompressing bytes
        2. Restoring an object from decompressed data
        """
        decompressed_data = self._compressor.decompress(data)
        decoded_data = self._bytes_converter.decode(decompressed_data)
        return decoded_data
