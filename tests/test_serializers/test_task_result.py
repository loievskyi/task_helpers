import pickle

from tests.conftest import mock_task_result_serializer


def test_serialize(mock_task_result_serializer):
    task_result = {"key": "value"}
    serialized_data = mock_task_result_serializer.serialize(task_result)
    excepted_data = pickle.dumps(task_result)
    assert serialized_data == excepted_data


def test_deserialize(mock_task_result_serializer):
    task_result = {"key": "value"}
    serialized_data = pickle.dumps(task_result)
    excepted = mock_task_result_serializer.deserialize(serialized_data)
    assert isinstance(excepted, dict)
    assert excepted["key"] == task_result["key"]


def test_serialize_deserialize_cycle(mock_task_result_serializer):
    task_result = {"key": "value"}
    serialized_data = mock_task_result_serializer.serialize(task_result)
    excepted = mock_task_result_serializer.deserialize(serialized_data)
    assert excepted == task_result
