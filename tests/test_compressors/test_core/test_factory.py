import pytest

from task_helpers.compressors import LeveledCompressor, Compressor
from task_helpers.compressors.core.enums import CompressionPolicy, CompressorType
from task_helpers.compressors.core.factory import CompressorFactory


def test_factory_creates_correct_compressor_types_with_default_policy():
    """Verifies that the factory creates compressors of correct types
    when using the default compression policy"""
    for compressor_type in CompressorType:
        compressor = CompressorFactory.create_compressor(compressor_type)
        assert isinstance(compressor, Compressor)
        assert isinstance(compressor, compressor_type.value)


@pytest.mark.parametrize("policy", list(CompressionPolicy))
def test_factory_respects_compression_policy_for_all_compressor_types(
        policy: CompressionPolicy
):
    """Verifies that the factory correctly applies compression policy
    to all supported compressor types"""
    for compressor_type in CompressorType:
        # Given
        compressor = CompressorFactory.create_compressor(
            compressor_type,
            policy
        )

        # Then
        assert isinstance(compressor, Compressor)
        assert isinstance(compressor, compressor_type.value)
        if isinstance(compressor, LeveledCompressor):
            expected_level = getattr(compressor, policy.value)
            assert compressor.level == expected_level
