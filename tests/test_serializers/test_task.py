import pytest

from task_helpers.tasks import Task
from .conftest import mock_task_serializer


def test_serialize(mock_task_serializer):
    task = Task(data="test_data")
    serialized_data = mock_task_serializer.serialize(task)
    excepted_data = mock_task_serializer._bytes_converter.encode((task.id.bytes, task.data))
    assert serialized_data == excepted_data


def test_deserialize(mock_task_serializer):
    task = Task(data="test_data")
    serialized_data = mock_task_serializer._bytes_converter.encode((task.id.bytes, task.data))
    excepted = mock_task_serializer.deserialize(serialized_data)
    assert isinstance(excepted, Task)
    assert excepted.data == task.data
    assert excepted.id == task.id


def test_serialize_deserialize_cycle(mock_task_serializer):
    task = Task(data="test_data")
    serialized_data = mock_task_serializer.serialize(task)
    excepted = mock_task_serializer.deserialize(serialized_data)
    assert excepted.data == task.data
    assert excepted.id == task.id


def test_serialize_with_invalid_task(mock_task_serializer):
    with pytest.raises(AttributeError):
        mock_task_serializer.serialize(None)
