import lzma
from .base import Compressor


class LzmaCompressor(Compressor):
    """Handles data compression using LZMA algorithm"""

    def __init__(self, level: int = 6):
        """
        Args:
            level: from 1 to 9, where:
                  0 = fastest compression
                  9 = maximum compression
        """
        if not 0 <= level <= 9:
            raise ValueError("LZMA compression level must be between 0 and 9")
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return lzma.compress(data, preset=self.level)

    def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)
