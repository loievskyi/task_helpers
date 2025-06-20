import pickle
from dataclasses import dataclass
from typing import List, Any

import pytest

from task_helpers.converters.bytes import PickleConverter


@dataclass
class SampleClass:
    name: str
    value: int


@pytest.fixture
def converter():
    return PickleConverter()


@pytest.fixture
def sample_objects():
    return [
        42,
        "test string",
        [1, 2, 3],
        {"key": "value"},
        (1, "tuple", True),
        {1, 2, 3},
        SampleClass("test", 42),
        None,
        True,
        3.14,
    ]


def test_should_correctly_encode_and_decode_simple_types(converter):
    test_cases = [
        42,
        "test string",
        True,
        None,
        3.14,
    ]

    for value in test_cases:
        encoded = converter.encode(value)
        assert isinstance(encoded, bytes)
        decoded = converter.decode(encoded)
        assert decoded == value
        assert type(decoded) == type(value)


def test_should_correctly_encode_and_decode_complex_types(converter, sample_objects):
    for obj in sample_objects:
        encoded = converter.encode(obj)
        assert isinstance(encoded, bytes)
        decoded = converter.decode(encoded)
        assert decoded == obj
        assert type(decoded) == type(obj)


def test_should_preserve_nested_structure(converter):
    nested_data = {
        "list": [1, 2, 3],
        "dict": {"inner": "value"},
        "tuple": (1, "test"),
        "object": SampleClass("nested", 100)
    }

    encoded = converter.encode(nested_data)
    decoded = converter.decode(encoded)

    assert decoded == nested_data
    assert isinstance(decoded["list"], list)
    assert isinstance(decoded["dict"], dict)
    assert isinstance(decoded["tuple"], tuple)
    assert isinstance(decoded["object"], SampleClass)


def test_should_raise_attribute_error_for_unpicklable_objects(converter):
    def unpicklable_function():
        pass

    with pytest.raises(AttributeError):
        converter.encode(unpicklable_function)


def test_should_raise_pickle_error_for_invalid_pickle_data(converter):
    invalid_data = b"not a valid pickle data"

    with pytest.raises(pickle.PickleError):
        converter.decode(invalid_data)


def test_should_handle_large_data_structures(converter):
    large_list = list(range(10000))
    large_dict = {str(i): i for i in range(10000)}

    test_cases = [large_list, large_dict]

    for value in test_cases:
        encoded = converter.encode(value)
        decoded = converter.decode(encoded)
        assert decoded == value
        assert type(decoded) == type(value)


def test_should_handle_recursive_structures(converter):
    recursive_list: List[Any] = [1, 2, 3]
    recursive_list.append(recursive_list)

    encoded = converter.encode(recursive_list)
    decoded = converter.decode(encoded)

    assert decoded[0] == 1
    assert decoded[1] == 2
    assert decoded[2] == 3
    assert decoded[3] is decoded


def test_should_maintain_object_identity(converter):
    shared_object = ["shared"]
    original = {
        "a": shared_object,
        "b": shared_object
    }

    encoded = converter.encode(original)
    decoded = converter.decode(encoded)

    assert decoded["a"] is decoded["b"]


def test_should_encode_and_decode_empty_containers(converter):
    empty_containers = [
        [],
        {},
        set(),
        (),
    ]

    for container in empty_containers:
        encoded = converter.encode(container)
        decoded = converter.decode(encoded)
        assert decoded == container
        assert type(decoded) == type(container)


def test_should_preserve_custom_attributes(converter):
    obj = SampleClass("test", 42)

    encoded = converter.encode(obj)
    decoded = converter.decode(encoded)

    assert decoded.name == "test"
    assert decoded.value == 42
    assert isinstance(decoded, SampleClass)
