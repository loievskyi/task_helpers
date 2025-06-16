import zlib
from .base import Compressor


class ZlibCompressor(Compressor):
    """Handles data compression using zlib algorithm"""

    def __init__(self, level: int = 6):
        """
        Args:
            level: from 0 to 9, where:
                  0 = no compression
                  1 = fastest compression
                  6 = default compression
                  9 = maximum compression
        """
        if not 0 <= level <= 9:
            raise ValueError("Zlib compression level must be between 0 and 9")
        self.level = level

    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data, level=self.level)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)
