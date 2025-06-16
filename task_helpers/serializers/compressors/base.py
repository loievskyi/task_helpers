from abc import ABC, abstractmethod
from enum import Enum
from typing import ClassVar


class Compressor(ABC):
    """Base interface for all compressors"""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress input data"""
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """Decompress input data"""
        pass


class LeveledCompressor(Compressor, ABC):
    """Base class for compressors that support compression levels"""

    MINIMAL_COMPRESSION_LEVEL: ClassVar[int]
    MEDIUM_COMPRESSION_LEVEL: ClassVar[int]
    MAXIMAL_COMPRESSION_LEVEL: ClassVar[int]

    def __init__(self, level: int) -> None:
        self._validate_level(level)
        self.level = level

    def _validate_level(self, level: int) -> None:
        if not self.MINIMAL_COMPRESSION_LEVEL <= level <= self.MAXIMAL_COMPRESSION_LEVEL:
            raise ValueError(
                f"Compression level must be between "
                f"{self.MINIMAL_COMPRESSION_LEVEL} and {self.MAXIMAL_COMPRESSION_LEVEL}"
            )


class CompressionPolicy(str, Enum):
    """Defines different compression policies"""
    NO_COMPRESSION = "no_compression"
    MINIMAL_COMPRESSION = "minimal_compression"
    MEDIUM_COMPRESSION = "medium_compression"
    MAXIMAL_COMPRESSION = "maximal_compression"
