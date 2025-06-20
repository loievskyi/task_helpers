from task_helpers.compressors.core.exceptions import CompressionError, UnsupportedCompressor


def test_compression_error():
    base_exc = ValueError("test error")
    exc = CompressionError(base_exc)
    assert exc.base_exception == base_exc


def test_unsupported_compressor():
    exc = UnsupportedCompressor(ValueError("unknown type"))
    assert isinstance(exc, CompressionError)
