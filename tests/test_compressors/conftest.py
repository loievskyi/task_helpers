import pytest

from task_helpers.compressors import Compressor, LeveledCompressor


class MockCompressor(Compressor):
    """Test implementation of Compressor"""

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


@pytest.fixture()
def mock_compressor() -> Compressor:
    """
    Returns a mock compressor that doesn't modify data
    """
    return MockCompressor()


class MockLeveledCompressor(LeveledCompressor):
    MINIMAL_COMPRESSION_LEVEL = 1
    MEDIUM_COMPRESSION_LEVEL = 5
    MAXIMAL_COMPRESSION_LEVEL = 9

    def compress(self, data: bytes) -> bytes:
        return data

    def decompress(self, data: bytes) -> bytes:
        return data


@pytest.fixture()
def mock_leveled_compressor() -> LeveledCompressor:
    """
    Returns a mock-leveled compressor that doesn't modify data
    """
    compression_level = MockLeveledCompressor.MEDIUM_COMPRESSION_LEVEL
    return MockLeveledCompressor(compression_level)
