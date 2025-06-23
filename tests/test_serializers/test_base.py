from tests.conftest import MockSerializer


def test_serialize():
    serializer = MockSerializer()
    input_data = "test_string"
    expected_output = b"test_string"
    assert serializer.serialize(input_data) == expected_output


def test_deserialize():
    serializer = MockSerializer()
    input_data = b"test_string"
    expected_output = "test_string"
    assert serializer.deserialize(input_data) == expected_output


def test_serialize_empty_string():
    serializer = MockSerializer()
    input_data = ""
    expected_output = b""
    assert serializer.serialize(input_data) == expected_output


def test_deserialize_empty_bytes():
    serializer = MockSerializer()
    input_data = b""
    expected_output = ""
    assert serializer.deserialize(input_data) == expected_output
