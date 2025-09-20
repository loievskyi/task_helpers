from task_helpers.backends.async_ import AsyncRedisBackend, AsyncBackend
from task_helpers.backends.sync import RedisBackend, Backend
from task_helpers.compressors import CompressorFactory, CompressorType
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.converters.bytes import MsgPackConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.converters.perform_task_error import PerformTaskErrorTupleConverter
from task_helpers.converters.stub import ConverterStub
from task_helpers.couriers import Courier, ClientSideCourier, WorkerSideCourier, AsyncClientSideCourier, AsyncWorkerSideCourier, \
    AsyncCourier
from task_helpers.serializers import TaskSerializer, CustomTypeSerializer


__all__ = [
    "CourierFactory",
    "SerializersFactory",
]


class SerializersFactory:
    @staticmethod
    def create_serializers(
            *, bytes_converter_class: type[BytesConverter] = MsgPackConverter,
            compressor_type: CompressorType = CompressorType.ZSTD,
            custom_type_converter_class: type[CustomTypeConverter] = CustomTypeConverter,
            perform_task_error_converter_class: type[PerformTaskErrorTupleConverter] = PerformTaskErrorTupleConverter
    ) -> tuple[TaskSerializer, CustomTypeSerializer]:
        converter_stub = ConverterStub()
        task_converter = TaskTupleConverter(task_data_converter=converter_stub)
        perform_task_error_converter = perform_task_error_converter_class(task_converter=task_converter)
        bytes_converter = bytes_converter_class()

        custom_type_converter = custom_type_converter_class(
            perform_task_error_converter=perform_task_error_converter,
            task_converter=task_converter,
            converter_stub=converter_stub,
        )
        setattr(task_converter, "_task_data_converter", custom_type_converter)

        compressor = CompressorFactory.create_compressor(compressor_type)

        task_serializer = TaskSerializer(
            task_converter=task_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )
        task_result_serializer = CustomTypeSerializer(
            custom_type_converter=custom_type_converter,
            bytes_converter=bytes_converter,
            compressor=compressor,
        )

        return task_serializer, task_result_serializer


class CourierFactory:
    @staticmethod
    def create(
            backend_connection, *,
            backend_class: type[Backend] = RedisBackend,
            bytes_converter_class: type[BytesConverter] = MsgPackConverter,
            compressor_type: CompressorType = CompressorType.ZSTD,
            custom_type_converter_class: type[CustomTypeConverter] = CustomTypeConverter,
            perform_task_error_converter_class: type[PerformTaskErrorTupleConverter] = PerformTaskErrorTupleConverter,
            courier_class: type[Courier | ClientSideCourier | WorkerSideCourier] = Courier,
    ) -> Courier | ClientSideCourier | WorkerSideCourier:
        task_serializer, task_result_serializer = SerializersFactory.create_serializers(
            bytes_converter_class=bytes_converter_class,
            compressor_type=compressor_type,
            custom_type_converter_class=custom_type_converter_class,
            perform_task_error_converter_class=perform_task_error_converter_class
        )

        return courier_class(
            task_serializer=task_serializer,
            task_result_serializer=task_result_serializer,
            backend=backend_class(backend_connection)
        )


class AsyncCourierFactory:
    @staticmethod
    def create(
            backend_connection, *,
            backend_class: type[AsyncBackend] = AsyncRedisBackend,
            bytes_converter_class: type[BytesConverter] = MsgPackConverter,
            compressor_type: CompressorType = CompressorType.ZSTD,
            custom_type_converter_class: type[CustomTypeConverter] = CustomTypeConverter,
            perform_task_error_converter_class: type[PerformTaskErrorTupleConverter] = PerformTaskErrorTupleConverter,
            courier_class: type[AsyncCourier | AsyncClientSideCourier | AsyncWorkerSideCourier] = AsyncCourier
    ) -> AsyncCourier | AsyncClientSideCourier | AsyncWorkerSideCourier:
        task_serializer, task_result_serializer = SerializersFactory.create_serializers(
            bytes_converter_class=bytes_converter_class,
            compressor_type=compressor_type,
            custom_type_converter_class=custom_type_converter_class,
            perform_task_error_converter_class=perform_task_error_converter_class
        )

        return courier_class(
            task_serializer=task_serializer,
            task_result_serializer=task_result_serializer,
            backend=backend_class(backend_connection)
        )
