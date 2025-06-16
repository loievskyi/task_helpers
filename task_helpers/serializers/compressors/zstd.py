import zstandard
from .base import Compressor


class ZstdCompressor(Compressor):
    """Handles data compression using the Zstandard algorithm"""

    def __init__(self, level: int = 3):
        """
        Args:
            level: Compression level (1-22). Higher = better compression but slower
        """
        self.compressor = zstandard.ZstdCompressor(level=level)
        self.decompressor = zstandard.ZstdDecompressor()

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using Zstandard"""
        return self.compressor.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress Zstandard-compressed bytes"""
        return self.decompressor.decompress(data)
