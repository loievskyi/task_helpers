import pickle
import uuid
import zlib
from abc import ABC, abstractmethod
from typing import TypeVar, Any

from task_helpers.tasks.task import Task

TypeObject = TypeVar("TypeObject")  # Type for serialization


class TupleConverter(ABC):
    """Converts an object to tuple and back"""

    @abstractmethod
    def to_tuple(self, obj: TypeObject) -> tuple:
        """Convert object to tuple representation"""
        pass

    @abstractmethod
    def from_tuple(self, data: tuple) -> TypeObject:
        """Restore object from tuple representation"""
        pass


class BytesConverter(ABC):
    """Converts data to bytes and back"""

    @abstractmethod
    def to_bytes(self, data: Any) -> bytes:
        """Convert tuple to byte representation"""
        pass

    @abstractmethod
    def from_bytes(self, data: bytes) -> Any:
        """Restore tuple from bytes representation"""
        pass


class Compressor(ABC):
    """Handles bytes compression"""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress bytes data"""
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """Decompress bytes data"""
        pass


class CompactSerializer:
    """Main class that combines all serialization stages"""

    def __init__(
            self,
            tuple_converter: TupleConverter,
            bytes_converter: BytesConverter,
            compressor: Compressor
    ):
        self._tuple_converter = tuple_converter
        self._bytes_converter = bytes_converter
        self._compressor = compressor

    def serialize(self, obj: TypeObject) -> bytes:
        """
        Serialize an object to compressed bytes

        The process includes:
        1. Converting an object to tuple
        2. Converting tuple to bytes
        3. Compressing bytes
        """
        tuple_data = self._tuple_converter.to_tuple(obj)
        bytes_data = self._bytes_converter.to_bytes(tuple_data)
        compressed_data = self._compressor.compress(bytes_data)
        return compressed_data

    def deserialize(self, data: bytes) -> TypeObject:
        """
        Deserialize an object from compressed bytes

        The process includes:
        1. Decompressing bytes
        2. Converting bytes to tuple
        3. Restoring an object from a tuple
        """
        decompressed_data = self._compressor.decompress(data)
        tuple_data = self._bytes_converter.from_bytes(decompressed_data)
        obj = self._tuple_converter.from_tuple(tuple_data)
        return obj


class TaskTupleConverter(TupleConverter):
    """Converts a Task object to and from tuple representation"""

    def to_tuple(self, task: Task) -> tuple:
        """Convert Task to minimal tuple representation"""
        return task.id.bytes, task.data

    def from_tuple(self, data: tuple) -> Task:
        """Restore Task from tuple representation"""
        task_id = uuid.UUID(bytes=data[0])
        return Task(id=task_id, data=data[1])


class PickleBytesConverter(BytesConverter):
    """Handles tuple conversion using pickle serialization"""

    def to_bytes(self, data: tuple) -> bytes:
        """Convert tuple to bytes using pickle"""
        return pickle.dumps(data)

    def from_bytes(self, data: bytes) -> tuple:
        """Restore tuple from pickled bytes"""
        return pickle.loads(data)


class ZlibCompressor(Compressor):
    """Handles data compression using zlib algorithm"""

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using zlib"""
        return zlib.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress zlib-compressed bytes"""
        return zlib.decompress(data)


def create_task_serializer() -> CompactSerializer:
    """
    Factory function to create the default task serializer
    with pickle serialization and zlib compression
    """
    return CompactSerializer(
        tuple_converter=TaskTupleConverter(),
        bytes_converter=PickleBytesConverter(),
        compressor=ZlibCompressor()
    )
