import pytest

from .conftest import converter


def test_encode_valid(converter):
    assert converter.encode("123") == 123
    assert converter.encode("-456") == -456
    assert converter.encode("0") == 0


def test_encode_invalid(converter):
    with pytest.raises(ValueError):
        converter.encode("hello")


def test_decode_valid(converter):
    assert converter.decode(123) == "123"
    assert converter.decode(-456) == "-456"
    assert converter.decode(0) == "0"


def test_round_trip_conversion(converter):
    source = "42"
    intermediate = converter.encode(source)
    result = converter.decode(intermediate)
    assert result == source
