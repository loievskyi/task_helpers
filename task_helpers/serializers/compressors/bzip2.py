import bz2
from .base import Compressor


class Bzip2Compressor(Compressor):
    """Handles data compression using bzip2 algorithm"""

    def __init__(self, level: int = 9):
        """
        Args:
            level: from 1 to 9, where:
                  1 = fastest compression
                  9 = maximum compression
        """
        if not 1 <= level <= 9:
            raise ValueError("Bzip2 compression level must be between 1 and 9")
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return bz2.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return bz2.decompress(data)
