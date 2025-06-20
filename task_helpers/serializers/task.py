from task_helpers.compressors import Compressor
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.tasks import Task
from .base import Serializer


class TaskSerializer(Serializer[Task, bytes]):
    """Main class that combines all serialization stages"""

    def __init__(
            self,
            tuple_converter: TaskTupleConverter,
            bytes_converter: BytesConverter,
            compressor: Compressor
    ):
        self._tuple_converter = tuple_converter
        self._bytes_converter = bytes_converter
        self._compressor = compressor

    def serialize(self, task: Task) -> bytes:
        """
        Serialize an object to compressed bytes

        The process includes:
        1. Converting an object to tuple
        2. Converting tuple to bytes
        3. Compressing bytes
        """
        tuple_data = self._tuple_converter.encode(task)
        bytes_data = self._bytes_converter.encode(tuple_data)
        compressed_data = self._compressor.compress(bytes_data)
        return compressed_data

    def deserialize(self, data: bytes) -> Task:
        """
        Deserialize an object from compressed bytes

        The process includes:
        1. Decompressing bytes
        2. Converting bytes to tuple
        3. Restoring an object from a tuple
        """
        decompressed_data = self._compressor.decompress(data)
        tuple_data = self._bytes_converter.decode(decompressed_data)
        task = self._tuple_converter.decode(tuple_data)
        return task
