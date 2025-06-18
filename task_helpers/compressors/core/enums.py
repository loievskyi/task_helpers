from enum import Enum
from typing import Type

from .base import Compressor
from .. import backends


class CompressionPolicy(str, Enum):
    """Defines different compression policies"""
    MINIMAL = "MINIMAL_COMPRESSION_LEVEL"
    MEDIUM = "MEDIUM_COMPRESSION_LEVEL"
    MAXIMAL = "MAXIMAL_COMPRESSION_LEVEL"


class CompressorType(Enum):
    BZIP2 = backends.Bzip2Compressor
    GZIP = backends.GzipCompressor
    LZ4 = backends.Lz4Compressor
    LZMA = backends.LzmaCompressor
    SNAPPY = backends.SnappyCompressor
    ZLIB = backends.ZlibCompressor
    ZSTD = backends.ZstdCompressor
    NO_COMPRESSION = backends.NoCompressionCompressor

    @property
    def compressor_class(self) -> Type[Compressor]:
        return self.value
