import pickle
from typing import Any

from ..base import Converter


class PickleConverter(Converter[Any, bytes]):
    def encode(self, source: Any) -> bytes:
        return pickle.dumps(source)

    def decode(self, target: bytes) -> Any:
        return pickle.loads(target)
