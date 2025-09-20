from .conftest import mock_custom_type_serializer


def test_serialize(mock_custom_type_serializer):
    task_result = {"key": "value"}
    serialized_data = mock_custom_type_serializer.serialize(task_result)
    assert isinstance(serialized_data, bytes)
    assert serialized_data != task_result


def test_serialize_deserialize_cycle(mock_custom_type_serializer):
    task_result = {"key": "value"}
    serialized_data = mock_custom_type_serializer.serialize(task_result)
    excepted = mock_custom_type_serializer.deserialize(serialized_data)
    assert excepted == task_result
    assert isinstance(excepted, dict)
    assert excepted["key"] == task_result["key"]
