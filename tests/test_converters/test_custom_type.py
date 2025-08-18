import uuid

from task_helpers.converters.stub import ConverterStub
from task_helpers.converters.task import TaskTupleConverter
from task_helpers.exceptions import PerformTaskError
from task_helpers.tasks import Task
from .conftest import custom_type_converter


def test_encode_task(custom_type_converter, random_text):
    task = Task(data=random_text)
    encoded = custom_type_converter.encode(task)

    assert isinstance(encoded, tuple)
    assert len(encoded) == 2
    assert encoded[0] == b"\x02"  # Prefix for Task
    assert isinstance(encoded[1], tuple)  # Encoded task


def test_encode_perform_task_error(custom_type_converter, random_text):
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
    assert encoded[0] == b"\x01"  # Prefix for PerformTaskError
    assert isinstance(encoded[1], tuple)


def test_encode_default_type(custom_type_converter):
    data = "Simple string"
    encoded = custom_type_converter.encode(data)

    assert isinstance(encoded, tuple)
    assert len(encoded) == 2
    assert encoded[0] == b"\x00"  # Default prefix
    assert encoded[1] == data  # ConverterStub doesn't change data


def test_decode_task(custom_type_converter, random_text):
    task_id = uuid.uuid4()
    task_data = random_text
    encoded_task = (task_id.bytes, task_data)
    encoded = (b"\x02", encoded_task)

    decoded = custom_type_converter.decode(encoded)

    assert isinstance(decoded, Task)
    assert decoded.id == task_id
    assert decoded.data == task_data


def test_decode_perform_task_error(custom_type_converter, random_text):
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
    encoded = (b"\x01", encoded_error)

    decoded = custom_type_converter.decode(encoded)

    assert isinstance(decoded, PerformTaskError)
    assert decoded.task is not None
    assert decoded.task.id == task_id
    assert decoded.task.data == task_data
    assert decoded.exception_data["class_name"] == "ValueError"
    assert decoded.exception_data["module_name"] == "builtins"
    assert decoded.exception_data["message"] == "Test error message"
    assert decoded.exception_data["traceback"] == "Test traceback"


def test_decode_default_type(custom_type_converter):
    data = "Simple string"
    encoded = (b"\x00", data)

    decoded = custom_type_converter.decode(encoded)

    assert decoded == data  # ConverterStub doesn't change data


def test_encode_decode_cycle_task(custom_type_converter, random_text):
    original_task = Task(data=random_text)

    encoded = custom_type_converter.encode(original_task)
    decoded = custom_type_converter.decode(encoded)

    assert isinstance(decoded, Task)
    assert decoded.id == original_task.id
    assert decoded.data == original_task.data


def test_encode_decode_cycle_perform_task_error(custom_type_converter, random_text):
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


def test_encode_decode_cycle_default_type(custom_type_converter):
    original_data = "Simple string"

    encoded = custom_type_converter.encode(original_data)
    decoded = custom_type_converter.decode(encoded)

    assert decoded == original_data


def test_set_task_converter(custom_type_converter):
    # Create a new task converter instance for replacement
    new_task_converter = TaskTupleConverter(ConverterStub())

    # Check that the set_task_converter method works
    custom_type_converter.set_task_converter(new_task_converter)

    # Verify that the new converter is used for tasks
    set_task_converter = custom_type_converter._task_converter
    assert set_task_converter is new_task_converter

    # Check that all works as expected
    task = Task(data="Test")
    encoded = custom_type_converter.encode(task)
    decoded = custom_type_converter.decode(encoded)

    assert isinstance(decoded, Task)
    assert decoded.id == task.id
    assert decoded.data == task.data
