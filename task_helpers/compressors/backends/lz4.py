import lz4.frame

from ..core.base import LeveledCompressor


class Lz4Compressor(LeveledCompressor):
    """Handles data compression using LZ4 algorithm"""

    MINIMAL_COMPRESSION_LEVEL = 0
    MEDIUM_COMPRESSION_LEVEL = 8
    MAXIMAL_COMPRESSION_LEVEL = 16

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using LZ4"""
        return lz4.frame.compress(data, compression_level=self.level)

    def decompress(self, data: bytes) -> bytes:
        """Decompress LZ4-compressed bytes"""
        return lz4.frame.decompress(data)
