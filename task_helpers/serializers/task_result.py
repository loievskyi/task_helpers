from typing import Any

from task_helpers.compressors import Compressor
from task_helpers.converters import BytesConverter
from .base import Serializer
from ..converters.perform_task_error_tuple import PerformTaskErrorTupleConverter
from ..exceptions import PerformTaskError


class TaskResultSerializer(Serializer[Any, bytes]):
    """Main class that combines all serialization stages"""

    def __init__(
            self,
            bytes_converter: BytesConverter,
            compressor: Compressor
    ):
        self._bytes_converter = bytes_converter
        self._compressor = compressor
        self._perform_task_error_converter = PerformTaskErrorTupleConverter()

    def serialize(self, task_result: Any) -> bytes:
        """
        Serialize an object to compressed bytes

        The process includes:
        1. Converting an object to bytes
        2. Compressing bytes
        """

        is_error = isinstance(task_result, PerformTaskError)

        if is_error:
            task_result = self._perform_task_error_converter.encode(task_result)

        bytes_data = self._bytes_converter.encode(task_result)
        compressed_data = self._compressor.compress(bytes_data)

        flag_byte = b"\x01" if is_error else b"\x00"
        return flag_byte + compressed_data

    def deserialize(self, data: bytes) -> Any:
        """
        Deserialize an object from compressed bytes

        The process includes:
        1. Decompressing bytes
        2. Restoring an object from decompressed data
        """

        flag_byte = data[0:1]
        is_error = flag_byte == b"\x01"
        compressed_data = data[1:]

        decompressed_data = self._compressor.decompress(compressed_data)
        decoded_data = self._bytes_converter.decode(decompressed_data)

        if is_error:
            decoded_data = self._perform_task_error_converter.decode(decoded_data)

        return decoded_data
