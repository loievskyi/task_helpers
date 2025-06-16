from .base import Compressor


class NoCompressionCompressor(Compressor):
    """Compressor that performs no compression"""

    def compress(self, data: bytes) -> bytes:
        """Return data as is without compression"""
        return data

    def decompress(self, data: bytes) -> bytes:
        """Return data as is without decompression"""
        return data
