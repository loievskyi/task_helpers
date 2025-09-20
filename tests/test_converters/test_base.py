import pytest

from .conftest import mock_converter


def test_encode_valid(mock_converter):
    assert mock_converter.encode("123") == 123
    assert mock_converter.encode("-456") == -456
    assert mock_converter.encode("0") == 0


def test_encode_invalid(mock_converter):
    with pytest.raises(ValueError):
        mock_converter.encode("hello")


def test_decode_valid(mock_converter):
    assert mock_converter.decode(123) == "123"
    assert mock_converter.decode(-456) == "-456"
    assert mock_converter.decode(0) == "0"


def test_round_trip_conversion(mock_converter):
    source = "42"
    intermediate = mock_converter.encode(source)
    result = mock_converter.decode(intermediate)
    assert result == source
