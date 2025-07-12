from task_helpers.backends.async_ import AsyncRedisBackend, AsyncBackend
from task_helpers.backends.sync import RedisBackend, Backend
from task_helpers.compressors import CompressorFactory, CompressorType
from task_helpers.converters import TaskTupleConverter, BytesConverter
from task_helpers.converters.bytes import PickleConverter
from task_helpers.couriers import Courier, ClientSideCourier, WorkerSideCourier, AsyncCourier, AsyncClientSideCourier, \
    AsyncWorkerSideCourier
from task_helpers.serializers import TaskSerializer, TaskResultSerializer


class CourierFactory:
    @staticmethod
    def create(backend_connection, *,
               backend_type: type[Backend] = RedisBackend,
               bytes_converter_type: type[BytesConverter] = PickleConverter,
               compressor_type: CompressorType = CompressorType.ZSTD) -> Courier | ClientSideCourier | WorkerSideCourier:
        return Courier(
            task_serializer=TaskSerializer(
                tuple_converter=TaskTupleConverter(),
                bytes_converter=bytes_converter_type(),
                compressor=CompressorFactory.create_compressor(compressor_type)
            ),
            task_result_serializer=TaskResultSerializer(
                bytes_converter=bytes_converter_type(),
                compressor=CompressorFactory.create_compressor(compressor_type)
            ),
            backend=backend_type(backend_connection)
        )


class AsyncCourierFactory:
    @staticmethod
    def create(backend_connection, *,
               backend_type: type[AsyncBackend] = AsyncRedisBackend,
               bytes_converter_type: type[BytesConverter] = PickleConverter,
               compressor_type: CompressorType = CompressorType.ZSTD) -> AsyncCourier | AsyncClientSideCourier | AsyncWorkerSideCourier:
        return AsyncCourier(
            task_serializer=TaskSerializer(
                tuple_converter=TaskTupleConverter(),
                bytes_converter=bytes_converter_type(),
                compressor=CompressorFactory.create_compressor(compressor_type)
            ),
            task_result_serializer=TaskResultSerializer(
                bytes_converter=bytes_converter_type(),
                compressor=CompressorFactory.create_compressor(compressor_type)
            ),
            backend=backend_type(backend_connection)
        )
