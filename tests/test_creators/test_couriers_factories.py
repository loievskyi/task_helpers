from unittest.mock import MagicMock

from task_helpers.backends.async_ import AsyncRedisBackend
from task_helpers.backends.sync import RedisBackend
from task_helpers.compressors import CompressorType
from task_helpers.converters.bytes import MsgPackConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.converters.perform_task_error import PerformTaskErrorTupleConverter
from task_helpers.couriers import (
    Courier, ClientSideCourier, WorkerSideCourier,
    AsyncCourier, AsyncClientSideCourier, AsyncWorkerSideCourier
)
from task_helpers.creators import SerializersFactory, CourierFactory, AsyncCourierFactory
from task_helpers.serializers import TaskSerializer, CustomTypeSerializer
from tests.test_backends.conftest import mock_redis_client
from .conftest import (
    BytesConverterMock, CustomTypeConverterMock, PerformTaskErrorConverterMock,
    CustomBackend, CustomAsyncBackend
)


class TestCourierFactory:
    def test_create_courier_with_defaults(self, mock_redis_client):
        """Test creating a courier with default parameters."""
        serializers = SerializersFactory.create_serializers()
        default_method = SerializersFactory.create_serializers

        SerializersFactory.create_serializers = MagicMock(
            return_value=serializers
        )

        # Create courier
        courier = CourierFactory.create(mock_redis_client)

        # Check types
        assert type(courier) is Courier
        assert type(courier._backend) is RedisBackend
        assert type(courier._task_serializer) is TaskSerializer
        assert type(courier._task_result_serializer) is CustomTypeSerializer

        # Check serializers
        SerializersFactory.create_serializers.assert_called_once_with(
            bytes_converter_class=MsgPackConverter,
            compressor_type=CompressorType.ZSTD,
            custom_type_converter_class=CustomTypeConverter,
            perform_task_error_converter_class=PerformTaskErrorTupleConverter
        )

        assert courier._task_serializer is serializers[0]
        assert courier._task_result_serializer is serializers[1]
        SerializersFactory.create_serializers = default_method


    def test_create_courier_with_custom_parameters(self, mock_redis_client):
        """Test creating a courier with custom parameters."""

        serializers = SerializersFactory.create_serializers(
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
        )

        default_method = SerializersFactory.create_serializers
        SerializersFactory.create_serializers = MagicMock(
            return_value=serializers
        )

        # Create courier
        courier = CourierFactory.create(
            mock_redis_client,
            backend_class=CustomBackend,
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
            courier_class=ClientSideCourier
        )

        # Check types
        assert type(courier) is ClientSideCourier
        assert type(courier._backend) is CustomBackend
        assert type(courier._task_serializer) is TaskSerializer
        assert type(courier._task_result_serializer) is CustomTypeSerializer

        # Check serializers
        SerializersFactory.create_serializers.assert_called_once_with(
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
        )

        assert courier._task_serializer is serializers[0]
        assert courier._task_result_serializer is serializers[1]
        SerializersFactory.create_serializers = default_method

    def test_create_worker_side_courier(self, mock_redis_client):
        """Test creating a worker-side courier."""

        # Create courier
        courier = CourierFactory.create(
            mock_redis_client,
            courier_class=WorkerSideCourier
        )

        # Check type
        assert isinstance(courier, WorkerSideCourier)

    def test_create_client_side_courier(self, mock_redis_client):
        """Test creating a worker-side courier."""

        # Create courier
        courier = CourierFactory.create(
            mock_redis_client,
            courier_class=ClientSideCourier
        )

        # Check type
        assert isinstance(courier, ClientSideCourier)


class TestAsyncCourierFactory:
    def test_create_courier_with_defaults(self, mock_redis_client):
        """Test creating a courier with default parameters."""
        serializers = SerializersFactory.create_serializers()

        default_method = SerializersFactory.create_serializers
        SerializersFactory.create_serializers = MagicMock(
            return_value=serializers
        )

        # Create courier
        courier = AsyncCourierFactory.create(mock_redis_client)

        # Check types
        assert type(courier) is AsyncCourier
        assert type(courier._backend) is AsyncRedisBackend
        assert type(courier._task_serializer) is TaskSerializer
        assert type(courier._task_result_serializer) is CustomTypeSerializer

        # Check serializers
        SerializersFactory.create_serializers.assert_called_once_with(
            bytes_converter_class=MsgPackConverter,
            compressor_type=CompressorType.ZSTD,
            custom_type_converter_class=CustomTypeConverter,
            perform_task_error_converter_class=PerformTaskErrorTupleConverter
        )

        assert courier._task_serializer is serializers[0]
        assert courier._task_result_serializer is serializers[1]
        SerializersFactory.create_serializers = default_method

    def test_create_courier_with_custom_parameters(self, mock_redis_client):
        """Test creating a courier with custom parameters."""

        serializers = SerializersFactory.create_serializers(
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
        )

        default_method = SerializersFactory.create_serializers
        SerializersFactory.create_serializers = MagicMock(
            return_value=serializers
        )

        # Create courier
        courier = AsyncCourierFactory.create(
            mock_redis_client,
            backend_class=CustomAsyncBackend,
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
            courier_class=AsyncClientSideCourier
        )

        # Check types
        assert type(courier) is AsyncClientSideCourier
        assert type(courier._backend) is CustomAsyncBackend
        assert type(courier._task_serializer) is TaskSerializer
        assert type(courier._task_result_serializer) is CustomTypeSerializer

        # Check serializers
        SerializersFactory.create_serializers.assert_called_once_with(
            bytes_converter_class=BytesConverterMock,
            compressor_type=CompressorType.NO_COMPRESSION,
            custom_type_converter_class=CustomTypeConverterMock,
            perform_task_error_converter_class=PerformTaskErrorConverterMock,
        )

        assert courier._task_serializer is serializers[0]
        assert courier._task_result_serializer is serializers[1]
        SerializersFactory.create_serializers = default_method

    def test_create_worker_side_courier(self, mock_redis_client):
        """Test creating a worker-side courier."""

        # Create courier
        courier = AsyncCourierFactory.create(
            mock_redis_client,
            courier_class=AsyncWorkerSideCourier
        )

        # Check type
        assert isinstance(courier, AsyncWorkerSideCourier)

    def test_create_client_side_courier(self, mock_redis_client):
        """Test creating a worker-side courier."""

        # Create courier
        courier = AsyncCourierFactory.create(
            mock_redis_client,
            courier_class=AsyncClientSideCourier
        )

        # Check type
        assert isinstance(courier, AsyncClientSideCourier)
