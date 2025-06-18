import pytest

from task_helpers.compressors.core.base import LeveledCompressor, Compressor


@pytest.fixture
def sample_data():
    return b"test data" * 1000


@pytest.fixture
def mock_compressor():
    class TestCompressor(Compressor):
        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return TestCompressor


@pytest.fixture
def mock_leveled_compressor():
    class TestLeveledCompressor(LeveledCompressor):
        MINIMAL_COMPRESSION_LEVEL = 1
        MEDIUM_COMPRESSION_LEVEL = 5
        MAXIMAL_COMPRESSION_LEVEL = 9

        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return TestLeveledCompressor
