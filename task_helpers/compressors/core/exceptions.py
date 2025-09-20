class CompressionError(Exception):
    """Base exception for compression operations"""

    def __init__(self, base_exception: Exception):
        self.base_exception = base_exception

class UnsupportedCompressor(CompressionError):
    """Requested compressor is not supported"""
    pass
