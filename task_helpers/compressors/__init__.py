"""Compression module providing a unified interface to various compression algorithms"""

from .core.base import Compressor, LeveledCompressor
from .core.enums import CompressionPolicy, CompressorType
from .core.factory import CompressorFactory
from .core.exceptions import CompressionError

__all__ = [
    # Core interfaces
    "Compressor",
    "LeveledCompressor",
    "CompressorFactory",

    # Enums
    "CompressionPolicy",
    "CompressorType",

    # Exceptions
    "CompressionError",
]
