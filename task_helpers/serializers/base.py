from abc import ABC, abstractmethod
from typing import TypeVar, Generic

SourceDataType = TypeVar("SourceDataType")
SerializedDataType = TypeVar("SerializedDataType")


class Serializer(ABC, Generic[SourceDataType, SerializedDataType]):
    """Base serializer interface for source and serialized"""

    @abstractmethod
    def serialize(self, source: SourceDataType) -> SerializedDataType:
        """Convert a source serialized to a serialized format"""

    @abstractmethod
    def deserialize(self, serialized: SerializedDataType) -> SourceDataType:
        """Convert serialized back to the original format"""
