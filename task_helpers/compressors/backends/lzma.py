import lzma

from ..core.base import LeveledCompressor


class LzmaCompressor(LeveledCompressor):
    """Handles data compression using LZMA algorithm"""

    MINIMAL_COMPRESSION_LEVEL = 0
    MEDIUM_COMPRESSION_LEVEL = 5
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return lzma.compress(data, preset=self.level)

    def decompress(self, data: bytes) -> bytes:
        return lzma.decompress(data)
