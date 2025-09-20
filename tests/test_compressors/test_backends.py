import pickle
import time
import uuid

import pytest

from task_helpers.compressors.core.enums import CompressionPolicy, CompressorType
from task_helpers.compressors.core.factory import CompressorFactory


class TestBackendsCompression:
    @pytest.fixture(params=[
        pytest.param(pickle.dumps((uuid.uuid4().bytes, "https://www.domain.com/path")), id="real_data"),
        pytest.param(b"small data", id="small_data"),
        pytest.param(b"medium data" * 100, id="medium_data"),
        pytest.param(b"large data" * 1000, id="large_data"),
    ])
    def test_data(self, request):
        return request.param

    @pytest.mark.parametrize("compressor_type", list(CompressorType))
    @pytest.mark.parametrize("policy", list(CompressionPolicy))
    def test_compress_and_decompress(self, compressor_type, policy: CompressionPolicy, test_data):
        # Given
        compressor = CompressorFactory.create_compressor(compressor_type, policy)

        # When
        compressed = compressor.compress(test_data)
        decompressed = compressor.decompress(compressed)

        # Then
        assert test_data == decompressed
        self._test_and_log_compression_metrics(compressor, policy, test_data)

    def _test_and_log_compression_metrics(self, compressor, policy, data):
        start_time = time.perf_counter()
        compressed = compressor.compress(data)
        compress_time = time.perf_counter() - start_time

        start_time = time.perf_counter()
        compressor.decompress(compressed)
        decompress_time = time.perf_counter() - start_time

        ratio = len(data) / len(compressed)
        compressor_name = compressor.__class__.__name__
        data_size = len(data)
        print(
            f"\nCompressor: {compressor_name}, "
            f"\npolicy: {policy}, "
            f"\nratio: {ratio:.5f}, "
            f"\ninput size: {data_size}, "
            f"\ncompressed size: {len(compressed)}, "
            f"\ncompress_time: {compress_time:.5f}, "
            f"\ndecompress_time: {decompress_time:.5f} "
            f"{'\nWarning: ineffective compression' if ratio < 1.0 else ''}\n"
        )
