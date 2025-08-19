from task_helpers.exceptions import (
    TaskHelperError, DoesNotExistError, TaskDoesNotExist,
    TaskResultDoesNotExist, PerformTaskError
)
from task_helpers.tasks import Task


def test_task_helper_error_hierarchy():
    """Test inheritance hierarchy of exceptions."""
    # Check base class inheritance
    assert issubclass(TaskHelperError, Exception)

    # Check inheritance from TaskHelperError
    assert issubclass(DoesNotExistError, TaskHelperError)

    # Check inheritance from DoesNotExistError
    assert issubclass(TaskDoesNotExist, DoesNotExistError)
    assert issubclass(TaskResultDoesNotExist, DoesNotExistError)


def test_perform_task_error_with_exception():
    """Test creating PerformTaskError with an exception."""
    try:
        # Generate an exception with traceback
        raise ValueError("Test error message")
    except ValueError as ex:
        # Create PerformTaskError from the exception
        error = PerformTaskError(exception=ex)

        # Verify exception is stored
        assert error.exception is ex

        # Verify exception data is extracted correctly
        assert error.exception_data["class_name"] == "ValueError"
        assert error.exception_data["module_name"] == "builtins"
        assert error.exception_data["message"] == "Test error message"
        assert isinstance(error.exception_data["traceback"], str)
        assert "raise ValueError" in error.exception_data["traceback"]


def test_perform_task_error_with_exception_data():
    """Test creating PerformTaskError with pre-defined exception data."""
    exception_data = {
        "class_name": "ValueError",
        "module_name": "builtins",
        "message": "Test error message",
        "traceback": "Test traceback",
    }

    error = PerformTaskError(exception_data=exception_data)

    # Verify exception is None
    assert error.exception is None

    # Verify exception data is stored correctly
    assert error.exception_data == exception_data


def test_perform_task_error_with_task():
    """Test creating PerformTaskError with a task."""
    task = Task(data="test_data")

    error = PerformTaskError(task=task)

    # Verify task is stored
    assert error.task is task


def test_perform_task_error_with_tuple_task():
    """Test creating PerformTaskError with a tuple task representation."""
    task_tuple = (b"123", "test_data")

    error = PerformTaskError(task=task_tuple)

    # Verify task tuple is stored
    assert error.task is task_tuple


def test_perform_task_error_combined():
    """Test creating PerformTaskError with exception, exception data, and task."""
    task = Task(data="test_data")

    try:
        raise ValueError("Test error message")
    except ValueError as exc:
        # Create PerformTaskError with all arguments
        error = PerformTaskError(
            exception=exc,
            exception_data={"custom": "data"},  # This should be overridden
            task=task
        )

        # Verify exception is stored
        assert error.exception is exc

        # Verify exception data from the exception overrides provided data
        assert error.exception_data["class_name"] == "ValueError"
        assert error.exception_data["module_name"] == "builtins"
        assert error.exception_data["message"] == "Test error message"
        assert "custom" not in error.exception_data

        # Verify task is stored
        assert error.task is task


def test_get_traceback_or_none_with_traceback():
    """Test _get_traceback_or_none with an exception that has a traceback."""
    try:
        # Generate an exception with traceback
        raise ValueError("Test error message")
    except ValueError as exc:
        error = PerformTaskError()
        traceback_str = error._get_traceback_or_none(exc)

        # Verify traceback is extracted
        assert isinstance(traceback_str, str)
        assert "raise ValueError" in traceback_str


def test_get_traceback_or_none_without_traceback():
    """Test _get_traceback_or_none with an exception without a traceback."""
    # Create an exception without raising it (no traceback)
    exc = ValueError("Test error message")

    error = PerformTaskError()
    traceback_str = error._get_traceback_or_none(exc)

    # Verify no traceback is returned
    assert traceback_str is None


def test_get_exception_data():
    """Test _get_exception_data method."""
    # Create an exception without raising it
    exception = ValueError("Test error message")

    error = PerformTaskError()
    exception_data = error._get_exception_data(exception)

    # Verify exception data is correctly extracted
    assert exception_data["class_name"] == "ValueError"
    assert exception_data["module_name"] == "builtins"
    assert exception_data["message"] == "Test error message"
    assert exception_data["traceback"] is None  # No traceback since we didn't raise


def test_perform_task_error_inheritance():
    """Test that PerformTaskError inherits from TaskHelperError."""
    error = PerformTaskError()

    assert isinstance(error, PerformTaskError)
    assert isinstance(error, TaskHelperError)
    assert isinstance(error, Exception)
