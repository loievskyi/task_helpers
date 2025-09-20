from typing import Type

from .base import LeveledCompressor, Compressor
from .enums import CompressionPolicy, CompressorType


class CompressorFactory:
    @staticmethod
    def create_compressor(compressor_type: CompressorType,
                          policy: CompressionPolicy = CompressionPolicy.MEDIUM) -> Compressor:
        compressor_class: Type[Compressor] = compressor_type.value
        if issubclass(compressor_class, LeveledCompressor):
            compression_level = getattr(compressor_class, policy.value)
            return compressor_class(level=compression_level)
        return compressor_class()
