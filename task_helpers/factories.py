from task_helpers.backends.async_ import AsyncRedisBackend, AsyncBackend
from task_helpers.backends.sync import RedisBackend, Backend
from task_helpers.compressors import CompressorFactory, CompressorType
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.converters.bytes import PickleConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.converters.perform_task_error import PerformTaskErrorTupleConverter
from task_helpers.converters.stub import ConverterStub
from task_helpers.couriers import Courier, ClientSideCourier, WorkerSideCourier, AsyncCourier, AsyncClientSideCourier, \
    AsyncWorkerSideCourier
from task_helpers.serializers import TaskSerializer, CustomTypeSerializer


class CourierFactory:
    @staticmethod
    def create(backend_connection, *,
               backend_type: type[Backend] = RedisBackend,
               bytes_converter_type: type[BytesConverter] = PickleConverter,
               compressor_type: CompressorType = CompressorType.ZSTD,
               custom_type_converter_type: type[CustomTypeConverter] = CustomTypeConverter,
               perform_task_error_converter_type: type[PerformTaskErrorTupleConverter] = PerformTaskErrorTupleConverter
               ) -> Courier | ClientSideCourier | WorkerSideCourier:
        stub_converter = ConverterStub()
        task_converter = TaskTupleConverter(stub_converter)
        bytes_converter = bytes_converter_type()
        compressor = CompressorFactory.create_compressor(compressor_type)
        perform_task_error_converter = perform_task_error_converter_type(task_converter)
        custom_type_converter = custom_type_converter_type(
            perform_task_error_converter=perform_task_error_converter,
            task_converter=task_converter,
            converter_stub=stub_converter,
        )

        task_serializer = TaskSerializer(
            task_converter=task_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )

        custom_type_serializer = CustomTypeSerializer(
            custom_type_converter=custom_type_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )

        return Courier(
            task_serializer=task_serializer,
            task_result_serializer=custom_type_serializer,
            backend=backend_type(backend_connection)
        )


class AsyncCourierFactory:
    @staticmethod
    def create(backend_connection, *,
               backend_type: type[Backend] = RedisBackend,
               bytes_converter_type: type[BytesConverter] = PickleConverter,
               compressor_type: CompressorType = CompressorType.ZSTD,
               custom_type_converter_type: type[CustomTypeConverter] = CustomTypeConverter,
               perform_task_error_converter_type: type[PerformTaskErrorTupleConverter] = PerformTaskErrorTupleConverter
               ) -> AsyncCourier | AsyncClientSideCourier | AsyncWorkerSideCourier:
        stub_converter = ConverterStub()
        task_converter = TaskTupleConverter(stub_converter)
        bytes_converter = bytes_converter_type()
        compressor = CompressorFactory.create_compressor(compressor_type)
        perform_task_error_converter = perform_task_error_converter_type(task_converter)
        custom_type_converter = custom_type_converter_type(
            perform_task_error_converter=perform_task_error_converter,
            task_converter=task_converter,
            converter_stub=stub_converter,
        )

        task_serializer = TaskSerializer(
            task_converter=task_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )

        custom_type_serializer = CustomTypeSerializer(
            custom_type_converter=custom_type_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )

        return AsyncCourier(
            task_serializer=task_serializer,
            task_result_serializer=custom_type_serializer,
            backend=backend_type(backend_connection)
        )
