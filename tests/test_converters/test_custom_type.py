import uuid
import pytest

from task_helpers.converters import Converter
from task_helpers.exceptions import PerformTaskError
from task_helpers.tasks import Task
from .conftest import custom_type_converter



class TestCustomTypeConverter:

    def test_encode_task(self, custom_type_converter, random_text):
        task = Task(data=random_text)
        encoded = custom_type_converter.encode(task)

        assert isinstance(encoded, tuple)
        assert len(encoded) == 2
        assert encoded[0] == self._task_prefix
        assert isinstance(encoded[1], tuple)  # Encoded task


    def test_encode_perform_task_error(self, custom_type_converter, random_text):
        task = Task(data=random_text)
        error = PerformTaskError(task=task, exception_data={
            "class_name": "ValueError",
            "module_name": "builtins",
            "message": "Test error message",
            "traceback": "Test traceback",
        })

        encoded = custom_type_converter.encode(error)

        assert isinstance(encoded, tuple)
        assert len(encoded) == 2
        assert encoded[0] == self._perform_task_error_prefix
        assert isinstance(encoded[1], tuple)


    def test_encode_default_type(self, custom_type_converter):
        data = "Simple string"
        encoded = custom_type_converter.encode(data)

        assert isinstance(encoded, tuple)
        assert len(encoded) == 2
        assert encoded[0] == self._default_prefix
        assert encoded[1] == data  # ConverterStub doesn't change data


    def test_decode_task(self, custom_type_converter, random_text):
        task_id = uuid.uuid4()
        task_data = random_text
        encoded_task = (task_id.bytes, task_data)
        encoded = (self._task_prefix, encoded_task)

        decoded = custom_type_converter.decode(encoded)

        assert isinstance(decoded, Task)
        assert decoded.id == task_id
        assert decoded.data == task_data


    def test_decode_perform_task_error(self, custom_type_converter, random_text):
        task_id = uuid.uuid4()
        task_data = random_text
        encoded_task = (task_id.bytes, task_data)

        encoded_exception_data = (
            "ValueError",
            "builtins",
            "Test error message",
            "Test traceback"
        )

        encoded_error = (encoded_task, encoded_exception_data)
        encoded = (self._perform_task_error_prefix, encoded_error)

        decoded = custom_type_converter.decode(encoded)

        assert isinstance(decoded, PerformTaskError)
        assert decoded.task is not None
        assert decoded.task.id == task_id
        assert decoded.task.data == task_data
        assert decoded.exception_data["class_name"] == "ValueError"
        assert decoded.exception_data["module_name"] == "builtins"
        assert decoded.exception_data["message"] == "Test error message"
        assert decoded.exception_data["traceback"] == "Test traceback"


    def test_decode_default_type(self, custom_type_converter):
        data = "Simple string"
        encoded = (self._default_prefix, data)

        decoded = custom_type_converter.decode(encoded)

        assert decoded == data  # ConverterStub doesn't change data


    def test_encode_decode_cycle_task(self, custom_type_converter, random_text):
        original_task = Task(data=random_text)

        encoded = custom_type_converter.encode(original_task)
        decoded = custom_type_converter.decode(encoded)

        assert isinstance(decoded, Task)
        assert decoded.id == original_task.id
        assert decoded.data == original_task.data


    def test_encode_decode_cycle_perform_task_error(self, custom_type_converter, random_text):
        task = Task(data=random_text)
        original_error = PerformTaskError(task=task, exception_data={
            "class_name": "ValueError",
            "module_name": "builtins",
            "message": "Test error message",
            "traceback": "Test traceback",
        })

        encoded = custom_type_converter.encode(original_error)
        decoded = custom_type_converter.decode(encoded)

        assert isinstance(decoded, PerformTaskError)
        assert decoded.task.id == original_error.task.id
        assert decoded.task.data == original_error.task.data
        assert decoded.exception_data["class_name"] == original_error.exception_data["class_name"]
        assert decoded.exception_data["module_name"] == original_error.exception_data["module_name"]
        assert decoded.exception_data["message"] == original_error.exception_data["message"]
        assert decoded.exception_data["traceback"] == original_error.exception_data["traceback"]


    def test_encode_decode_cycle_default_type(self, custom_type_converter):
        original_data = "Simple string"

        encoded = custom_type_converter.encode(original_data)
        decoded = custom_type_converter.decode(encoded)

        assert decoded == original_data


    def test_add_converter(self, custom_type_converter):
        # Create a custom type and converter
        class CustomType:
            def __init__(self, value):
                self.value = value

        class CustomTypeToStrConverter(Converter[CustomType, str]):
            def encode(self, source):
                return str(source.value)

            def decode(self, target):
                return CustomType(target)

        # Add the converter to the CustomTypeConverter
        converter = CustomTypeToStrConverter()
        custom_type_converter.prefix_size = 5
        custom_type_converter._add_converter(CustomType, converter)

        assert custom_type_converter._type_prefix_map[CustomType] == b"\x00\x00\x00\x00\x03"
        assert custom_type_converter._prefix_encoders_map[b"\x00\x00\x00\x00\x03"] is converter


    def test_added_converter_converts_correctly(self, custom_type_converter):
        # Create a custom type and converter
        class CustomType:
            def __init__(self, value):
                self.value = value

        class CustomTypeToStrConverter(Converter[CustomType, str]):
            def encode(self, source):
                return str(source.value)

            def decode(self, target):
                return CustomType(target)

        # Add the converter to the CustomTypeConverter
        converter = CustomTypeToStrConverter()
        custom_type_converter._add_converter(CustomType, converter)

        # Test encoding and decoding with the new converter
        original = CustomType(42)
        encoded = custom_type_converter.encode(original)

        # Check prefix
        assert encoded[0] == b"\x03"

        # Check encoded value
        assert encoded[1] == "42"

        # Test decoding
        decoded = custom_type_converter.decode(encoded)
        assert isinstance(decoded, CustomType)
        assert decoded.value == "42"  # String because our converter converts to string


    def test_add_converter_duplicate_type_raises_assertion_error(self, custom_type_converter):
        """Test that adding a converter for an already registered type raises an AssertionError."""
        # Try to add a converter for a Task type, which is already registered
        class TaskConverter(Converter[Task, dict]):
            def encode(self, source):
                return {"id": str(source.id), "data": source.data}

            def decode(self, target):
                return Task(id=uuid.UUID(target["id"]), data=target["data"])

        converter = TaskConverter()

        # The assertion should be raised because Task is already registered
        with pytest.raises(AssertionError) as ex:
            custom_type_converter._add_converter(Task, converter)

        assert "Type already exists" in str(ex.value)


    @property
    def _task_prefix(self):
        return b"\x01"

    @property
    def _perform_task_error_prefix(self):
        return b"\x02"

    @property
    def _default_prefix(self):
        return b"\x00"
