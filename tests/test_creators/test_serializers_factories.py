from unittest.mock import MagicMock

import pytest

from task_helpers.backends.async_ import AsyncRedisBackend
from task_helpers.backends.sync import RedisBackend
from task_helpers.compressors import CompressorType
from task_helpers.compressors.backends import NoCompressionCompressor
from task_helpers.converters import TaskTupleConverter
from task_helpers.converters.bytes import MsgPackConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.couriers import (
    Courier, ClientSideCourier, WorkerSideCourier,
    AsyncCourier, AsyncClientSideCourier, AsyncWorkerSideCourier
)
from task_helpers.creators import SerializersFactory, CourierFactory, AsyncCourierFactory
from task_helpers.exceptions import PerformTaskError
from task_helpers.serializers import TaskSerializer, CustomTypeSerializer
from .conftest import (
    BytesConverterMock, CustomTypeConverterMock, PerformTaskErrorConverterMock
)


class TestSerializersFactory:
    def test_create_serializers_with_defaults(self):
        """Test creating serializers with default parameters."""
        task_serializer, custom_type_serializer = SerializersFactory.create_serializers()

        # Check types
        assert type(task_serializer) is TaskSerializer
        assert type(custom_type_serializer) is CustomTypeSerializer

        # Check converters
        assert type(task_serializer._task_converter) is TaskTupleConverter
        assert type(custom_type_serializer._custom_type_converter) is CustomTypeConverter

        assert type(task_serializer._bytes_converter) is MsgPackConverter
        assert type(custom_type_serializer._bytes_converter) is MsgPackConverter

        # Check compressor
        assert type(task_serializer._compressor) is CompressorType.ZSTD.value
        assert type(custom_type_serializer._compressor) is CompressorType.ZSTD.value

        # Check that the same compressor is used for both serializers
        assert task_serializer._compressor is custom_type_serializer._compressor

    def test_create_serializers_with_custom_parameters(self):
        """Test creating serializers with custom parameters."""

        task_serializer, custom_type_serializer = SerializersFactory.create_serializers(
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
        )

        # Check types
        assert type(task_serializer) is TaskSerializer
        assert type(custom_type_serializer) is CustomTypeSerializer

        # Check converters
        assert type(task_serializer._task_converter) is TaskTupleConverter
        assert type(custom_type_serializer._custom_type_converter) is CustomTypeConverterMock

        assert type(task_serializer._bytes_converter) is BytesConverterMock
        assert type(custom_type_serializer._bytes_converter) is BytesConverterMock

        # Check compressor
        assert type(task_serializer._compressor) is NoCompressionCompressor
        assert type(custom_type_serializer._compressor) is NoCompressionCompressor

        custom_type_converter = custom_type_serializer._custom_type_converter
        prefix = custom_type_converter._type_prefix_map[PerformTaskError]
        assert type(custom_type_converter._prefix_encoders_map[prefix]) is PerformTaskErrorConverterMock

        # Check that the same compressor is used for both serializers
        assert task_serializer._compressor is custom_type_serializer._compressor


class TestSerializersIntegration:
    def test_task_data_converter_circular_reference(self):
        """Test that the task_data_converter circular reference is set up correctly."""
        task_serializer, custom_type_serializer = SerializersFactory.create_serializers()

        # The task converter should use the custom type converter for serializing task data,
        # and the custom type converter should use the task converter for serializing tasks
        task_converter = task_serializer._task_converter
        custom_type_converter = task_converter._task_data_converter

        # Check that custom_type_converter knows about task_converter
        assert hasattr(custom_type_converter, "_prefix_encoders_map")
        assert isinstance(custom_type_converter, CustomTypeConverter)

        # Find the Task converter in the prefix_encoders_map
        task_prefix = None
        for prefix, converter in custom_type_converter._prefix_encoders_map.items():
            if converter is task_converter:
                task_prefix = prefix
                break

        assert task_prefix is not None, "Task converter not found in custom type converter"


@pytest.mark.parametrize("factory_class,courier_class,backend_class", [
    (CourierFactory, Courier, RedisBackend),
    (CourierFactory, ClientSideCourier, RedisBackend),
    (CourierFactory, WorkerSideCourier, RedisBackend),
    (AsyncCourierFactory, AsyncCourier, AsyncRedisBackend),
    (AsyncCourierFactory, AsyncClientSideCourier, AsyncRedisBackend),
    (AsyncCourierFactory, AsyncWorkerSideCourier, AsyncRedisBackend),
])
def test_create_couriers_all_types(factory_class, courier_class, backend_class):
    """Test creating all types of couriers."""
    # Mock Redis connection
    mock_connection = MagicMock()

    # Create courier
    courier = factory_class.create(
        mock_connection,
        courier_class=courier_class
    )

    # Check types
    assert type(courier) is courier_class
    assert type(courier._backend) is backend_class
