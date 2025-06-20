from task_helpers.compressors import Compressor
from task_helpers.compressors.core.enums import CompressorType, CompressionPolicy


def test_compressor_type_values():
    for compressor_type in CompressorType:
        assert issubclass(compressor_type.value, Compressor)


def test_compressor_type_compressor_class():
    for compressor_type in CompressorType:
        assert compressor_type.compressor_class == compressor_type.value


def test_compression_policy_values():
    expected_policies = {
        CompressionPolicy.MINIMAL: "MINIMAL_COMPRESSION_LEVEL",
        CompressionPolicy.MEDIUM: "MEDIUM_COMPRESSION_LEVEL",
        CompressionPolicy.MAXIMAL: "MAXIMAL_COMPRESSION_LEVEL"
    }

    for policy, value in expected_policies.items():
        assert policy.value == value
