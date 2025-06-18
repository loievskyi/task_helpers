import pytest
from task_helpers.compressors.core.base import LeveledCompressor


class TestLeveledCompressor(LeveledCompressor):
    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 5
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


def test_leveled_compressor_initialization():
    # Test valid compression levels
    TestLeveledCompressor(1)  # minimal
    TestLeveledCompressor(5)  # medium
    TestLeveledCompressor(6)
    TestLeveledCompressor(9)  # maximal

    # Test invalid compression levels
    with pytest.raises(ValueError):
        TestLeveledCompressor(0)  # below minimal
    with pytest.raises(ValueError):
        TestLeveledCompressor(10)  # above maximal


def test_compressor_level_property():
    compressor = TestLeveledCompressor(5)
    assert compressor.level == 5
