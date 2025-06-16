from abc import ABC, abstractmethod


class Compressor(ABC):
    """Handles bytes compression"""

    @abstractmethod
    def compress(self, data: bytes) -> bytes:
        """Compress bytes data"""
        pass

    @abstractmethod
    def decompress(self, data: bytes) -> bytes:
        """Decompress bytes data"""
        pass


class ConfigurableCompressor(Compressor):
    """Wrapper for other compressors that allows compression level configuration"""

    def __init__(self, base_compressor: Compressor, level: int):
        self.base_compressor = base_compressor
        self.level = level

    def compress(self, data: bytes) -> bytes:
        if hasattr(self.base_compressor, "level"):
            self.base_compressor.level = self.level
        return self.base_compressor.compress(data)

    def decompress(self, data: bytes) -> bytes:
        return self.base_compressor.decompress(data)


class NoCompression(Compressor):
    """Wrapper for other compressors that allows compression level configuration"""
    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data
