import zstandard

from ..core.base import LeveledCompressor


class ZstdCompressor(LeveledCompressor):
    """Handles data compression using the Zstandard algorithm"""

    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 3
    MAXIMAL_COMPRESSION_LEVEL = 22

    def __init__(self, level: int = 3):
        """
        Args:
            level: Compression level (1-22). Higher = better compression but slower
        """
        super().__init__(level)
        self.compressor = zstandard.ZstdCompressor(level=level)
        self.decompressor = zstandard.ZstdDecompressor()

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using Zstandard"""
        return self.compressor.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress Zstandard-compressed bytes"""
        return self.decompressor.decompress(data)
