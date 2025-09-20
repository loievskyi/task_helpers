import time
import uuid

from task_helpers.tasks import Task, ExtendedTask


def test_task_creation_with_defaults():
    """Test creating a Task with default values."""
    data = "test_data"
    task = Task(data=data)

    # Check data is set correctly
    assert task.data == data

    # Check id is auto-generated as UUID
    assert isinstance(task.id, uuid.UUID)

    # Check result is None by default
    assert task.result is None


def test_task_creation_with_custom_id():
    """Test creating a Task with a custom UUID."""
    data = "test_data"
    custom_id = uuid.uuid4()
    task = Task(data=data, id=custom_id)

    # Check data is set correctly
    assert task.data == data

    # Check custom id is used
    assert task.id == custom_id

    # Check result is None by default
    assert task.result is None


def test_task_with_result():
    """Test creating a Task with a result."""
    data = "test_data"
    result = "test_result"
    task = Task(data=data, result=result)

    # Check data and result are set correctly
    assert task.data == data
    assert task.result == result


def test_task_with_complex_data():
    """Test creating a Task with complex data types."""
    # Dictionary data
    dict_data = {"key": "value", "nested": {"inner": 42}}
    task = Task(data=dict_data)
    assert task.data == dict_data

    # List data
    list_data = [1, 2, 3, {"key": "value"}]
    task = Task(data=list_data)
    assert task.data == list_data

    # Object data
    class CustomObject:
        def __init__(self, value):
            self.value = value

    obj_data = CustomObject(42)
    task = Task(data=obj_data)
    assert task.data is obj_data
    assert task.data.value == 42


def test_extended_task_creation_with_defaults():
    """Test creating an ExtendedTask with default values."""
    data = "test_data"

    # Mock time.time to return a fixed value
    before_creation_time = time.time()
    task = ExtendedTask(data=data)
    after_creation_time = time.time()
    assert before_creation_time < task.created_at < after_creation_time

    # Check data is set correctly
    assert task.data == data

    # Check id is auto-generated
    assert isinstance(task.id, uuid.UUID)

    # Check default values
    assert task.result is None
    assert task.started_at is None
    assert task.finish_at is None
    assert task.error is None
    assert task.retries == 0


def test_extended_task_with_custom_values():
    """Test creating an ExtendedTask with custom values."""
    data = "test_data"
    custom_id = uuid.uuid4()
    result = "test_result"
    created_at = 1000.0
    started_at = 1001.0
    finish_at = 1002.0
    error = ValueError("Test error")
    retries = 3

    task = ExtendedTask(
        data=data,
        id=custom_id,
        result=result,
        created_at=created_at,
        started_at=started_at,
        finish_at=finish_at,
        error=error,
        retries=retries
    )

    # Check all values are set correctly
    assert task.data == data
    assert task.id == custom_id
    assert task.result == result
    assert task.created_at == created_at
    assert task.started_at == started_at
    assert task.finish_at == finish_at
    assert task.error == error
    assert task.retries == retries


def test_extended_task_inherits_from_task():
    """Test that ExtendedTask is a subclass of Task."""
    task = ExtendedTask(data="test")

    assert isinstance(task, ExtendedTask)
    assert isinstance(task, Task)


def test_created_at_default_is_current_time():
    """Test that created_at default is the current time."""
    # Get current time before and after creating the task
    time_before = time.time()
    task = ExtendedTask(data="test")
    time_after = time.time()

    # Check created_at is between time_before and time_after
    assert time_before <= task.created_at <= time_after


def test_task_equality():
    """Test Task equality based on its dataclass implementation."""
    # Create two tasks with the same ID and data
    task_id = uuid.uuid4()
    task1 = Task(data="test", id=task_id)
    task2 = Task(data="test", id=task_id)

    # They should be equal because dataclasses implement __eq__
    assert task1 == task2

    # Create another task with different data but the same ID
    task3 = Task(data="different", id=task_id)

    # They should be different
    assert task1 != task3

    # Create another task with the same data but different ID
    task4 = Task(data="test")

    # They should be different
    assert task1 != task4


def test_extended_task_equality():
    """Test ExtendedTask equality based on its dataclass implementation."""
    # Create two extended tasks with the same values
    task_id = uuid.uuid4()
    task1 = ExtendedTask(
        data="test",
        id=task_id,
        created_at=1000.0,
        started_at=1001.0,
        finish_at=1002.0
    )
    task2 = ExtendedTask(
        data="test",
        id=task_id,
        created_at=1000.0,
        started_at=1001.0,
        finish_at=1002.0
    )

    # They should be equal
    assert task1 == task2

    # Create another task with one different value
    task3 = ExtendedTask(
        data="test",
        id=task_id,
        created_at=1000.0,
        started_at=1001.0,
        finish_at=1003.0  # Different finish time
    )

    # They should be different
    assert task1 != task3
