import gzip
from .base import Compressor


class GzipCompressor(Compressor):
    """Handles data compression using gzip algorithm"""

    def __init__(self, level: int = 9):
        """
        Args:
            level: from 0 to 9, where:
                  0 = no compression
                  1 = fastest compression
                  9 = maximum compression
        """
        if not 0 <= level <= 9:
            raise ValueError("Gzip compression level must be between 0 and 9")
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return gzip.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return gzip.decompress(data)
