from ..core.base import Compressor


class NoCompressionCompressor(Compressor):
    """CompressorType that performs no compression"""

    def compress(self, data: bytes) -> bytes:
        """Return data as is without compression"""
        return data

    def decompress(self, data: bytes) -> bytes:
        """Return data as is without decompression"""
        return data
