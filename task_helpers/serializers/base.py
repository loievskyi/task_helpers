from abc import ABC, abstractmethod
from typing import TypeVar, Generic

SourceType = TypeVar("SourceType")
TargetType = TypeVar("TargetType")


class Serializer(ABC, Generic[SourceType, TargetType]):
    """Base serializer interface with generic source and target types"""

    @abstractmethod
    def serialize(self, data: SourceType) -> TargetType:
        """Convert source data to the target format"""

    @abstractmethod
    def deserialize(self, data: TargetType) -> SourceType:
        """Restore source data from target format"""
