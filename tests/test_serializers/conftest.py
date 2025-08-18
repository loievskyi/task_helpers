import pytest

from task_helpers.serializers import CustomTypeSerializer
from task_helpers.serializers.base import Serializer
from task_helpers.serializers.task import TaskSerializer
from tests.test_converters.conftest import task_converter, bytes_converter, custom_type_converter, converter_stub
from tests.test_compressors.conftest import mock_compressor


converter_stub = converter_stub  # pytest not seen converter_stub fixture without this

class MockStrSerializer(Serializer[str, bytes]):
    def serialize(self, data: str) -> bytes:
        return data.encode("utf-8")

    def deserialize(self, data: bytes) -> str:
        return data.decode("utf-8")


@pytest.fixture
def str_bytes_serializer():
    return MockStrSerializer()


@pytest.fixture
def mock_task_serializer(task_converter, bytes_converter, mock_compressor) -> TaskSerializer:
    return TaskSerializer(
        task_converter=task_converter,
        bytes_converter=bytes_converter,
        compressor=mock_compressor,
    )


@pytest.fixture
def mock_custom_type_serializer(custom_type_converter, bytes_converter, mock_compressor) -> CustomTypeSerializer:
    return CustomTypeSerializer(
        custom_type_converter=custom_type_converter,
        bytes_converter=bytes_converter,
        compressor=mock_compressor,
    )
