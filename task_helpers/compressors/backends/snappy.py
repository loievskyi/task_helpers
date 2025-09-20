import snappy

from ..core.base import Compressor


class SnappyCompressor(Compressor):
    """Handles data compression using Snappy algorithm"""

    def compress(self, data: bytes) -> bytes:
        """Compress bytes using Snappy"""
        return snappy.compress(data)

    def decompress(self, data: bytes) -> bytes:
        """Decompress Snappy-compressed bytes"""
        return snappy.decompress(data)
