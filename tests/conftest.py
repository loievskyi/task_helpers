import random
import string
from typing import Callable, Type

import pytest

from task_helpers.compressors.core.base import LeveledCompressor, Compressor


@pytest.fixture
def sample_data() -> bytes:
    """Returns repeating test data with a known pattern"""
    return b"test data" * 1000


@pytest.fixture
def random_text_generator(min_length: int = 10, max_length: int = 100) -> Callable[[], str]:
    """
    Returns a function that generates random text strings
    """
    def _generate() -> str:
        length = random.randint(min_length, max_length)
        return "".join(random.choice(string.ascii_letters) for _ in range(length))
    return _generate


@pytest.fixture
def random_text(random_text_generator) -> str:
    """
    Returns a single random text string
    """
    return random_text_generator()


@pytest.fixture()
def mock_compressor_class() -> Type[Compressor]:
    """
    Returns a mock compressor class that doesn't modify data
    """
    class MockCompressor(Compressor):
        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return MockCompressor


@pytest.fixture()
def mock_compressor(mock_compressor_class: Type[Compressor]) -> Compressor:
    """
    Returns a mock compressor that doesn't modify data
    """
    return mock_compressor_class()


@pytest.fixture()
def mock_leveled_compressor_class() -> Type[LeveledCompressor]:
    """
    Returns a mock-leveled compressor class that doesn't modify data
    """
    class MockLeveledCompressor(LeveledCompressor):
        MINIMAL_COMPRESSION_LEVEL = 1
        MEDIUM_COMPRESSION_LEVEL = 5
        MAXIMAL_COMPRESSION_LEVEL = 9

        def compress(self, data: bytes) -> bytes:
            return data

        def decompress(self, data: bytes) -> bytes:
            return data

    return MockLeveledCompressor


@pytest.fixture()
def mock_leveled_compressor(mock_leveled_compressor_class: Type[LeveledCompressor]) -> LeveledCompressor:
    """
    Returns a mock-leveled compressor that doesn't modify data
    """
    compression_level = mock_leveled_compressor_class.MEDIUM_COMPRESSION_LEVEL
    return mock_leveled_compressor_class(compression_level)
