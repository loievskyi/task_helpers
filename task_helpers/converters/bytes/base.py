from abc import ABC

from ..base import Converter, SourceType


class BytesConverter(Converter[SourceType, bytes], ABC):
    pass
