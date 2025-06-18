"""Compression module providing a unified interface to various compression algorithms"""

from .core import Compressor, LeveledCompressor, CompressorFactory, compressors_enums
from .core.enums import CompressionPolicy, CompressorType

__all__ = [
    # Core interfaces
    "Compressor",
    "LeveledCompressor",
    "CompressorFactory",

    # Enums
    "CompressionPolicy",
    "CompressorType",
]
