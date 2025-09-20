import pickle
from typing import Any

from .base import BytesConverter, Converter


class PickleConverter(BytesConverter, Converter[Any, bytes]):
    def encode(self, source: Any) -> bytes:
        return pickle.dumps(source)

    def decode(self, target: bytes) -> Any:
        return pickle.loads(target)
