from abc import abstractmethod, ABC
from typing import TypeVar, Generic


SourceType = TypeVar("SourceType")    # Original object type to convert from
TargetType = TypeVar("TargetType")    # Target format type to convert to


class Converter(Generic[SourceType, TargetType], ABC):
    """Converts between source object and target representation"""

    @abstractmethod
    def encode(self, source: SourceType) -> TargetType:
        """Convert a source object to target representation"""

    @abstractmethod
    def decode(self, target: TargetType) -> SourceType:
        """Restore a source object from target representation"""
