import pickle
import random
import string
import uuid
from typing import Callable, Type, Any, Tuple

import pytest

from task_helpers.compressors.core.base import LeveledCompressor, Compressor
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.serializers.base import Serializer
from task_helpers.serializers.task import TaskSerializer
from task_helpers.serializers.task_result import TaskResultSerializer
from task_helpers.tasks import Task


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


class MockSerializer(Serializer[str, bytes]):
    def serialize(self, data: str) -> bytes:
        return data.encode("utf-8")

    def deserialize(self, data: bytes) -> str:
        return data.decode("utf-8")


@pytest.fixture
def mock_task_serializer(mock_task_tuple_converter, mock_bytes_converter, mock_compressor) -> TaskSerializer:
    return TaskSerializer(
        tuple_converter=mock_task_tuple_converter,
        bytes_converter=mock_bytes_converter,
        compressor=mock_compressor,
    )


@pytest.fixture
def mock_task_result_serializer(mock_bytes_converter, mock_compressor) -> TaskResultSerializer:
    return TaskResultSerializer(
        bytes_converter=mock_bytes_converter,
        compressor=mock_compressor,
    )


class MockTaskTupleConverter(TaskTupleConverter):
    def encode(self, source: Task) -> tuple[bytes, Any]:
        return source.id.bytes, source.data

    def decode(self, target: tuple[bytes, Any]) -> Task:
        task_id = uuid.UUID(bytes=target[0])
        return Task(id=task_id, data=target[1])


@pytest.fixture
def mock_task_tuple_converter() -> TaskTupleConverter:
    return MockTaskTupleConverter()


class BytesConverterMock(BytesConverter):
    def encode(self, source) -> bytes:
        return pickle.dumps(source)

    def decode(self, target: bytes) -> Any:
        return pickle.loads(target)


@pytest.fixture
def mock_bytes_converter() -> BytesConverter:
    return BytesConverterMock()
