from task_helpers.backends.async_ import AsyncBackend
from task_helpers.backends.sync import Backend
from task_helpers.converters import BytesConverter
from task_helpers.converters.custom_type import CustomTypeConverter
from task_helpers.converters.perform_task_error import PerformTaskErrorTupleConverter
from task_helpers.exceptions import DoesNotExistError


class BytesConverterMock(BytesConverter):
    def encode(self, source):
        return source

    def decode(self, target):
        return target


class CustomTypeConverterMock(CustomTypeConverter):
    pass


class PerformTaskErrorConverterMock(PerformTaskErrorTupleConverter):
    pass


# Mock custom backend
class CustomBackend(Backend):
    def pop_from_queue(self, queue_name, error_class=DoesNotExistError): pass

    def pop_from_queue_blocking(self, queue_name, timeout_seconds=None): pass

    def bulk_pop_from_queue(self, queue_name, max_count): pass

    def move_between_queues(self, source_queue_name, target_queue_name, error_class=DoesNotExistError): pass

    def move_between_queues_blocking(self, source_queue_name, target_queue_name, timeout_seconds=None): pass

    def pop_or_requeue(self, queue_name, delete_data=True, error_class=DoesNotExistError): pass

    def pop_or_requeue_blocking(self, queue_name, delete_data=True, timeout_seconds=None): pass

    def exists(self, key): pass

    def set(self, key, value): pass

    def add_to_queue(self, queue_name, data): pass

    def bulk_add_to_queue(self, queue_name, data): pass

    def expire(self, key, seconds): pass

    def pipeline(self): pass

    def get(self, key): pass


# Mock custom async backend
class CustomAsyncBackend(AsyncBackend):
    async def pop_from_queue(self, queue_name, error_class=DoesNotExistError): pass

    async def pop_from_queue_blocking(self, queue_name, timeout_seconds=None): pass

    async def bulk_pop_from_queue(self, queue_name, max_count): pass

    async def move_between_queues(self, source_queue_name, target_queue_name, error_class=DoesNotExistError): pass

    async def move_between_queues_blocking(self, source_queue_name, target_queue_name, timeout_seconds=None): pass

    async def pop_or_requeue(self, queue_name, delete_data=True, error_class=DoesNotExistError): pass

    async def pop_or_requeue_blocking(self, queue_name, delete_data=True, timeout_seconds=None): pass

    async def exists(self, key): pass

    async def set(self, key, value): pass

    async def add_to_queue(self, queue_name, data): pass

    async def bulk_add_to_queue(self, queue_name, data): pass

    async def expire(self, key, seconds): pass

    async def pipeline(self): pass

    async def get(self, key): pass
