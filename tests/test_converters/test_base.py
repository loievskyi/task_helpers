import pytest

from task_helpers.converters.base import Converter


class MockConverter(Converter[str, int]):
    def encode(self, source: str) -> int:
        return int(source)

    def decode(self, target: int) -> str:
        return str(target)


def test_encode_valid():
    converter = MockConverter()
    assert converter.encode("123") == 123
    assert converter.encode("-456") == -456
    assert converter.encode("0") == 0


def test_encode_invalid():
    converter = MockConverter()
    with pytest.raises(ValueError):
        converter.encode("hello")


def test_decode_valid():
    converter = MockConverter()
    assert converter.decode(123) == "123"
    assert converter.decode(-456) == "-456"
    assert converter.decode(0) == "0"


def test_round_trip_conversion():
    converter = MockConverter()
    source = "42"
    intermediate = converter.encode(source)
    result = converter.decode(intermediate)
    assert result == source
