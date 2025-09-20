import pytest

from tests.conftest import random_text
from ..conftest import MockCompressor, MockLeveledCompressor


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
