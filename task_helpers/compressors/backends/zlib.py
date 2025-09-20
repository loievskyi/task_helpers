import zlib

from ..core.base import LeveledCompressor


class ZlibCompressor(LeveledCompressor):
    """Handles data compression using zlib algorithm"""

    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 6
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return zlib.compress(data, level=self.level)

    def decompress(self, data: bytes) -> bytes:
        return zlib.decompress(data)
