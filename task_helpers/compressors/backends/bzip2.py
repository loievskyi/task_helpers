import bz2

from ..core.base import LeveledCompressor


class Bzip2Compressor(LeveledCompressor):
    """Handles data compression using bzip2 algorithm"""

    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 5
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return bz2.compress(data, compresslevel=self.level)

    def decompress(self, data: bytes) -> bytes:
        return bz2.decompress(data)
