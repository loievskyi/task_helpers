import pytest
from task_helpers.compressors.core.base import LeveledCompressor, Compressor


class MockCompressor(Compressor):
    """Test implementation of Compressor"""
    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


class MockLeveledCompressor(LeveledCompressor):
    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 5
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


def test_compressor_compress_decompress(random_text: str):
    compressor = MockCompressor()
    data = random_text.encode()
    compressed_data = compressor.compress(data)
    decompressed_data = compressor.decompress(compressed_data)
    assert data == decompressed_data


def test_leveled_compressor_initialization():
    # Test valid compression levels
    MockLeveledCompressor(1)  # minimal
    MockLeveledCompressor(5)  # medium
    MockLeveledCompressor(6)
    MockLeveledCompressor(9)  # maximal

    # Test invalid compression levels
    with pytest.raises(ValueError):
        MockLeveledCompressor(0)  # below minimal
    with pytest.raises(ValueError):
        MockLeveledCompressor(10)  # above maximal


def test_leveled_compressor_compress_decompress(random_text: str):
    compression_level = MockLeveledCompressor.MEDIUM_COMPRESSION_LEVEL
    compressor = MockLeveledCompressor(compression_level)
    data = random_text.encode()
    compressed_data = compressor.compress(data)
    decompressed_data = compressor.decompress(compressed_data)
    assert data == decompressed_data


def test_compressor_level_property():
    compressor = MockLeveledCompressor(5)
    assert compressor.level == 5
