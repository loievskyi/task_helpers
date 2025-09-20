from task_helpers.compressors import Compressor
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.tasks import Task
from .base import Serializer


class TaskSerializer(Serializer[Task, bytes]):
    def __init__(
            self,
            task_converter: TaskTupleConverter,
            bytes_converter: BytesConverter,
            compressor: Compressor
    ):
        self._task_converter = task_converter
        self._bytes_converter = bytes_converter
        self._compressor = compressor

    def serialize(self, source: Task) -> bytes:
        """
        Serialize an object to compressed bytes

        The process includes:
        1. Converting an object to tuple
        2. Converting tuple to bytes
        3. Compressing bytes
        """
        encoded = self._task_converter.encode(source)
        encoded = self._bytes_converter.encode(encoded)
        return self._compressor.compress(encoded)

    def deserialize(self, serialized: bytes) -> Task:
        """
        Deserialize an object from compressed bytes

        The process includes:
        1. Decompressing bytes
        2. Converting bytes to tuple
        3. Restoring an object from a tuple
        """
        partially_deserialized = self._compressor.decompress(serialized)
        partially_deserialized = self._bytes_converter.decode(partially_deserialized)
        return self._task_converter.decode(partially_deserialized)
