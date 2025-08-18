import uuid

from task_helpers.tasks import Task
from task_helpers.exceptions import PerformTaskError
from .conftest import random_text, perform_task_error_converter




def test_encode_perform_task_error_with_task(perform_task_error_converter, random_text):
    task = Task(data=random_text)
    error = PerformTaskError(task=task, exception_data={
        "class_name": "ValueError",
        "module_name": "builtins",
        "message": "Test error message",
        "traceback": "Test traceback",
    })

    encoded = perform_task_error_converter.encode(error)

    assert isinstance(encoded, tuple)
    assert len(encoded) == 2
    assert isinstance(encoded[0], tuple)  # encoded task
    assert isinstance(encoded[1], tuple)  # encoded exception data
    assert len(encoded[1]) == 4  # 4 fields in exception data


def test_encode_perform_task_error_without_task(perform_task_error_converter):
    error = PerformTaskError(exception_data={
        "class_name": "ValueError",
        "module_name": "builtins",
        "message": "Test error message",
        "traceback": "Test traceback",
    })

    encoded = perform_task_error_converter.encode(error)

    assert isinstance(encoded, tuple)
    assert len(encoded) == 2
    assert encoded[0] is None  # task is None
    assert isinstance(encoded[1], tuple)  # encoded exception data
    assert len(encoded[1]) == 4  # 4 fields in exception data


def test_decode_perform_task_error_with_task(perform_task_error_converter, random_text):
    task_id = uuid.uuid4()
    task_data = random_text
    encoded_task = (task_id.bytes, task_data)

    encoded_exception_data = (
        "ValueError",
        "builtins",
        "Test error message",
        "Test traceback"
    )

    encoded = (encoded_task, encoded_exception_data)

    error = perform_task_error_converter.decode(encoded)

    assert isinstance(error, PerformTaskError)
    assert error.task is not None
    assert error.task.id == task_id
    assert error.task.data == task_data
    assert error.exception_data["class_name"] == "ValueError"
    assert error.exception_data["module_name"] == "builtins"
    assert error.exception_data["message"] == "Test error message"
    assert error.exception_data["traceback"] == "Test traceback"


def test_decode_perform_task_error_without_task(perform_task_error_converter):
    encoded_exception_data = (
        "ValueError",
        "builtins",
        "Test error message",
        "Test traceback"
    )

    encoded = (None, encoded_exception_data)

    error = perform_task_error_converter.decode(encoded)

    assert isinstance(error, PerformTaskError)
    assert error.task is None
    assert error.exception_data["class_name"] == "ValueError"
    assert error.exception_data["module_name"] == "builtins"
    assert error.exception_data["message"] == "Test error message"
    assert error.exception_data["traceback"] == "Test traceback"


def test_encode_decode_cycle_with_task(perform_task_error_converter, random_text):
    task = Task(data=random_text)
    original_error = PerformTaskError(task=task, exception_data={
        "class_name": "ValueError",
        "module_name": "builtins",
        "message": "Test error message",
        "traceback": "Test traceback",
    })

    encoded = perform_task_error_converter.encode(original_error)
    decoded = perform_task_error_converter.decode(encoded)

    assert decoded.task.id == original_error.task.id
    assert decoded.task.data == original_error.task.data
    assert decoded.exception_data["class_name"] == original_error.exception_data["class_name"]
    assert decoded.exception_data["module_name"] == original_error.exception_data["module_name"]
    assert decoded.exception_data["message"] == original_error.exception_data["message"]
    assert decoded.exception_data["traceback"] == original_error.exception_data["traceback"]


def test_encode_decode_cycle_without_task(perform_task_error_converter):
    original_error = PerformTaskError(exception_data={
        "class_name": "ValueError",
        "module_name": "builtins",
        "message": "Test error message",
        "traceback": "Test traceback",
    })

    encoded = perform_task_error_converter.encode(original_error)
    decoded = perform_task_error_converter.decode(encoded)

    assert decoded.task is None
    assert decoded.exception_data["class_name"] == original_error.exception_data["class_name"]
    assert decoded.exception_data["module_name"] == original_error.exception_data["module_name"]
    assert decoded.exception_data["message"] == original_error.exception_data["message"]
    assert decoded.exception_data["traceback"] == original_error.exception_data["traceback"]
