import lz4.frame
from .base import Compressor


class Lz4Compressor(Compressor):
    """Handles data compression using LZ4 algorithm"""

    def __init__(self, level: int = 9):
        """
        Args:
            level: from 1 to 16, where:
                  0 = fastest compression
                  16 = maximum compression
        """
        if not 0 <= level <= 16:
            raise ValueError("lz4 compression level must be between 0 and 16")
        self.level = level

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using LZ4"""
        return lz4.frame.compress(data, compression_level=self.level)

    def decompress(self, data: bytes) -> bytes:
        """Decompress LZ4-compressed bytes"""
        return lz4.frame.decompress(data)
