from .conftest import str_bytes_serializer


def test_serialize(str_bytes_serializer):
    input_data = "test_string"
    expected_output = b"test_string"
    assert str_bytes_serializer.serialize(input_data) == expected_output


def test_deserialize(str_bytes_serializer):
    input_data = b"test_string"
    expected_output = "test_string"
    assert str_bytes_serializer.deserialize(input_data) == expected_output


def test_serialize_empty_string(str_bytes_serializer):
    input_data = ""
    expected_output = b""
    assert str_bytes_serializer.serialize(input_data) == expected_output


def test_deserialize_empty_bytes(str_bytes_serializer):
    input_data = b""
    expected_output = ""
    assert str_bytes_serializer.deserialize(input_data) == expected_output
